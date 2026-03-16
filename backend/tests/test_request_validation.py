import unittest

from flask import Flask, jsonify, request

try:
    from request_validation import parse_json_body
except ImportError:
    from backend.request_validation import parse_json_body


class ParseJsonBodyTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

        @self.app.route("/echo", methods=["POST"])
        def echo():
            data, error = parse_json_body(request, required_fields=["input_text"])
            if error:
                payload, status = error
                return jsonify(payload), status
            return jsonify({"output": data["input_text"]}), 200

        self.client = self.app.test_client()

    def test_rejects_non_json_content_type(self):
        response = self.client.post("/echo", data="input_text=test")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
            "error": "Request must be JSON",
            "status": 400,
        })

    def test_rejects_empty_json_object(self):
        response = self.client.post("/echo", json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
            "error": "JSON body cannot be empty",
            "status": 400,
        })

    def test_rejects_malformed_json_payload(self):
        response = self.client.post(
            "/echo",
            data='{"input_text":',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
            "error": "Malformed JSON payload",
            "status": 400,
        })

    def test_rejects_missing_required_fields(self):
        response = self.client.post("/echo", json={"use_mediawiki": 0})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
            "error": "Missing required field(s): input_text",
            "status": 400,
        })

    def test_accepts_valid_json_payload(self):
        response = self.client.post("/echo", json={"input_text": "AI text"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"output": "AI text"})


if __name__ == "__main__":
    unittest.main()