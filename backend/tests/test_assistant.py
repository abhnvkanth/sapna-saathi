import asyncio
import io
import json
from urllib.error import HTTPError, URLError
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ai_service
import main
from pydantic import ValidationError


class AssistantTests(unittest.TestCase):
    def test_chat_rejects_blank_and_overlong_questions(self) -> None:
        with self.assertRaises(ValidationError):
            main.ChatRequest(question="   ")
        with self.assertRaises(ValidationError):
            main.ChatRequest(question="x" * 1501)

    def test_chat_uses_labelled_fallback_without_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            result = asyncio.run(ai_service.chat("When is the deadline?", [], {}))
        self.assertEqual(result["mode"], "demo_fallback")
        self.assertIn("Demo guidance", result["label"])
        self.assertIn("verified live deadline", result["answer"])

    def test_document_guidance_fallback_is_document_specific(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            result = asyncio.run(ai_service.guidance("marksheet", {}))
        self.assertEqual(result["mode"], "demo_fallback")
        self.assertIn("school office", result["answer"])

    def test_provider_context_excludes_personal_fields(self) -> None:
        with patch.dict(os.environ, {"SAPNA_AI_API_KEY": "test-only"}), patch.object(ai_service, "_call_provider", return_value="A demo response.") as provider:
            result = asyncio.run(ai_service.chat("How do I begin?", [], {"class_level": "12th pass", "course": "Arts", "name": "Private Name", "income": "secret-value", "district": "Private District"}))
        sent = provider.call_args.args[0][0]["content"]
        self.assertEqual(result["mode"], "llm")
        self.assertIn("12th pass", sent)
        self.assertNotIn("Private Name", sent)
        self.assertNotIn("secret-value", sent)
        self.assertNotIn("Private District", sent)

    def test_provider_rejects_non_https_remote_url(self) -> None:
        with patch.dict(os.environ, {"SAPNA_AI_API_KEY": "test-only", "SAPNA_AI_MODEL": "test-model", "SAPNA_AI_BASE_URL": "http://localhost.attacker.invalid/chat"}), patch.object(ai_service, "urlopen") as open_url:
            with self.assertRaises(RuntimeError):
                ai_service._call_provider([])
        open_url.assert_not_called()

    def test_groq_endpoint_and_model_are_configurable(self) -> None:
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b'{"choices":[{"message":{"content":"Test response"}}]}'
        with patch.dict(os.environ, {"SAPNA_AI_API_KEY": "test-only", "SAPNA_AI_BASE_URL": ai_service.DEFAULT_PROVIDER_URL, "SAPNA_AI_MODEL": "currently-selected-test-model"}), patch.object(ai_service, "urlopen", return_value=response) as open_url:
            self.assertEqual(ai_service._call_provider([]), "Test response")
        request = open_url.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.groq.com/openai/v1/chat/completions")
        request_body = json.loads(request.data)
        self.assertEqual(request_body["model"], "currently-selected-test-model")
        self.assertEqual(request_body["temperature"], 0.3)
        self.assertEqual(request_body["max_tokens"], 350)

    def test_missing_model_uses_safe_fallback(self) -> None:
        with patch.dict(os.environ, {"SAPNA_AI_API_KEY": "test-only"}, clear=True), patch.object(ai_service, "urlopen") as open_url:
            result = asyncio.run(ai_service.chat("How do I begin?", [], {}))
        self.assertEqual(result["mode"], "demo_fallback")
        self.assertIn("provider unavailable", result["label"])
        open_url.assert_not_called()

    def test_diagnostics_log_presence_and_sanitized_provider_failure(self) -> None:
        secret_marker = "never-log-this-key"
        failure = HTTPError("https://provider.invalid/?token=private", 429, "limited", None, io.BytesIO(b'{"error":{"code":429,"message":"temporary busy"}}'))
        with patch.dict(os.environ, {"SAPNA_AI_API_KEY": secret_marker, "SAPNA_AI_MODEL": "test-model"}), patch.object(ai_service, "urlopen", side_effect=failure), patch.object(ai_service.time, "sleep"):
            with self.assertLogs(ai_service.logger, level="WARNING") as captured:
                with self.assertRaises(RuntimeError):
                    ai_service._call_provider([])
        joined = " ".join(captured.output)
        self.assertIn("AI provider error code=429", joined)
        self.assertNotIn(secret_marker, joined)
        self.assertNotIn("private", joined)
        self.assertIn("temporary busy", joined)

    def test_gemini_503_retries_then_succeeds(self) -> None:
        failure = HTTPError("https://generativelanguage.googleapis.com/", 503, "unavailable", None, io.BytesIO(b'{"error":{"code":503,"status":"UNAVAILABLE","message":"temporarily unavailable"}}'))
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b'{"choices":[{"message":{"content":"Gemini response"}}]}'
        with patch.dict(os.environ, {"SAPNA_AI_API_KEY": "test-only", "SAPNA_AI_BASE_URL": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", "SAPNA_AI_MODEL": "gemini-3.8-flash"}), patch.object(ai_service, "urlopen", side_effect=[failure, response]) as open_url, patch.object(ai_service.time, "sleep") as sleep:
            with self.assertLogs(ai_service.logger, level="WARNING") as captured:
                result = ai_service._call_provider([{"role": "user", "content": "safe question"}])
        self.assertEqual(result, "Gemini response")
        self.assertEqual(open_url.call_count, 2)
        request = open_url.call_args_list[0].args[0]
        self.assertEqual(request.full_url, "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-only")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        request_body = json.loads(request.data)
        self.assertEqual(request_body["model"], "gemini-3.8-flash")
        self.assertEqual(request_body["messages"], [{"role": "user", "content": "safe question"}])
        self.assertEqual(set(request_body), {"model", "messages"})
        sleep.assert_called_once_with(ai_service.RETRY_INITIAL_DELAY_SECONDS)
        logged = " ".join(captured.output)
        self.assertIn("AI provider error code=503", logged)
        self.assertIn("temporarily unavailable", logged)
        self.assertNotIn("safe question", logged)

    def test_429_retry_is_bounded_with_exponential_backoff(self) -> None:
        errors = [HTTPError("https://provider.invalid/", 429, "limited", None, io.BytesIO(b'{"error":{"message":"rate limited"}}')) for _ in range(ai_service.MAX_PROVIDER_ATTEMPTS)]
        with patch.dict(os.environ, {"SAPNA_AI_API_KEY": "test-only", "SAPNA_AI_MODEL": "test-model"}), patch.object(ai_service, "urlopen", side_effect=errors) as open_url, patch.object(ai_service.time, "sleep") as sleep:
            with self.assertLogs(ai_service.logger, level="WARNING"):
                with self.assertRaises(RuntimeError):
                    ai_service._call_provider([])
        self.assertEqual(open_url.call_count, ai_service.MAX_PROVIDER_ATTEMPTS)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [0.25, 0.5])

    def test_transient_network_error_retries(self) -> None:
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b'{"choices":[{"message":{"content":"Recovered"}}]}'
        with patch.dict(os.environ, {"SAPNA_AI_API_KEY": "test-only", "SAPNA_AI_MODEL": "gemini-test"}), patch.object(ai_service, "urlopen", side_effect=[URLError("private network detail"), response]) as open_url, patch.object(ai_service.time, "sleep"):
            with self.assertLogs(ai_service.logger, level="WARNING") as captured:
                result = ai_service._call_provider([])
        self.assertEqual(result, "Recovered")
        self.assertEqual(open_url.call_count, 2)
        self.assertIn("category=network", " ".join(captured.output))
        self.assertNotIn("private network detail", " ".join(captured.output))

    def test_http_error_message_redacts_question_and_credentials(self) -> None:
        credential_marker = "fake-api-key-marker-for-test"
        question = "My personal question with name Ananya"
        failure = HTTPError("https://provider.invalid/", 503, "unavailable", None, io.BytesIO(json.dumps({"error": {"code": 503, "message": f"{question}; API key={credential_marker}; contact 9876543210"}}).encode()))
        with patch.dict(os.environ, {"SAPNA_AI_API_KEY": credential_marker, "SAPNA_AI_MODEL": "test-model"}), patch.object(ai_service, "urlopen", side_effect=failure), patch.object(ai_service.time, "sleep"):
            with self.assertLogs(ai_service.logger, level="WARNING") as captured:
                with self.assertRaises(RuntimeError):
                    ai_service._call_provider([{"role": "user", "content": question}])
        logged = " ".join(captured.output)
        self.assertNotIn(question, logged)
        self.assertNotIn(credential_marker, logged)
        self.assertNotIn("9876543210", logged)
        self.assertIn("[redacted]", logged)

    def test_http_401_and_invalid_provider_payload_fall_back(self) -> None:
        cases = [
            (HTTPError("https://provider.invalid/", 401, "unauthorized", None, None), "AI provider error code=401", None),
            (MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b"not-json")))), "category=invalid_response", None),
        ]
        for error, expected_log, status in cases:
            with self.subTest(expected_log=expected_log), patch.dict(os.environ, {"SAPNA_AI_API_KEY": "test-only", "SAPNA_AI_MODEL": "test-model"}), patch.object(ai_service, "urlopen", side_effect=error):
                with self.assertLogs(ai_service.logger, level="WARNING") as captured:
                    result = asyncio.run(ai_service.chat("How do I begin?", [], {}))
            self.assertEqual(result["mode"], "demo_fallback")
            joined = " ".join(captured.output)
            self.assertIn(expected_log, joined)
            if status:
                self.assertIn(status, joined)

    def test_eligibility_remains_deterministic_and_independent_of_ai(self) -> None:
        profile = main.Profile(classLevel="12th pass", course="BA / BSc", income="150000", rural=True, marks="72")
        request = main.EligibilityRequest(profile=profile)
        with patch.object(ai_service, "chat", side_effect=AssertionError("eligibility must not call AI")):
            results = main.check_eligibility(request)
        self.assertEqual([result["opportunity_id"] for result in results], ["post", "rural", "kanya"])
        self.assertTrue(all(result["eligible"] for result in results))


if __name__ == "__main__":
    unittest.main()
