import json
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

import httpx

from handelsregister import Handelsregister
from handelsregister.exceptions import AuthenticationError, HandelsregisterError, InvalidResponseError


class TestClientInitialization:
    def test_init_with_api_key(self, api_key):
        """Test client initialization with explicit API key."""
        client = Handelsregister(api_key=api_key)
        assert client.api_key == api_key
        assert client.base_url == "https://handelsregister.ai/api/v1"

    def test_init_with_env_var(self):
        """Test client initialization with API key from environment."""
        env_api_key = "env_test_key_67890"
        with patch.dict(os.environ, {"HANDELSREGISTER_API_KEY": env_api_key}):
            client = Handelsregister()
            assert client.api_key == env_api_key

    def test_init_without_api_key(self):
        """Test that initialization fails without API key."""
        with patch.dict(os.environ, {"HANDELSREGISTER_API_KEY": ""}):
            with pytest.raises(AuthenticationError):
                Handelsregister()

    def test_init_with_custom_values(self, api_key):
        """Test initialization with custom timeout and base URL."""
        custom_timeout = 30.0
        custom_base_url = "https://custom.handelsregister.ai/api/v2/"
        
        client = Handelsregister(
            api_key=api_key,
            timeout=custom_timeout,
            base_url=custom_base_url
        )
        
        assert client.timeout == custom_timeout
        assert client.base_url == "https://custom.handelsregister.ai/api/v2"  # Trailing slash stripped


class TestFetchOrganization:
    def test_fetch_organization_basic(self, mock_client, sample_organization_response):
        """Test basic fetch_organization call."""
        client, mock_httpx = mock_client
        
        # Configure mock response
        mock_response = MagicMock()
        mock_response.json.return_value = sample_organization_response
        mock_response.raise_for_status.return_value = None
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_httpx.return_value.__enter__.return_value = mock_session
        
        # Call the method
        result = client.fetch_organization(q="OroraTech GmbH")
        
        # Verify results
        assert result == sample_organization_response
        mock_session.get.assert_called_once()
        
        # Check that parameters were passed correctly
        args, kwargs = mock_session.get.call_args
        assert kwargs["params"]["q"] == "OroraTech GmbH"
        assert kwargs["params"]["api_key"] == client.api_key

    def test_fetch_organization_with_features(self, mock_client, sample_organization_response):
        """Test fetch_organization with feature flags."""
        client, mock_httpx = mock_client
        
        # Configure mock response
        mock_response = MagicMock()
        mock_response.json.return_value = sample_organization_response
        mock_response.raise_for_status.return_value = None
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_httpx.return_value.__enter__.return_value = mock_session
        
        # Call the method with features
        features = ["related_persons", "publications"]
        result = client.fetch_organization(q="Test GmbH", features=features)
        
        # Verify results
        assert result == sample_organization_response
        
        # Check features were passed correctly
        args, kwargs = mock_session.get.call_args
        assert kwargs["params"]["feature"] == features

    def test_missing_query_parameter(self, mock_client):
        """Test that fetch_organization raises an error without a query."""
        client, _ = mock_client
        
        with pytest.raises(ValueError, match="Parameter 'q' is required"):
            client.fetch_organization(q="")

    def test_authentication_error(self, mock_client):
        """Test handling of authentication errors."""
        client, mock_httpx = mock_client
        
        # Configure mock response for 401 Unauthorized
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=MagicMock(status_code=401)
        )
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_httpx.return_value.__enter__.return_value = mock_session
        
        # Call the method and expect AuthenticationError
        with pytest.raises(AuthenticationError):
            client.fetch_organization(q="Test Company")

    def test_non_json_response(self, mock_client):
        """Test handling of invalid JSON responses."""
        client, mock_httpx = mock_client
        
        # Configure mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_httpx.return_value.__enter__.return_value = mock_session
        
        # Call the method and expect InvalidResponseError
        with pytest.raises(InvalidResponseError):
            client.fetch_organization(q="Test Company")


class TestHelperMethods:
    def test_build_q_string(self):
        """Test building query strings from item properties."""
        client = Handelsregister(api_key="dummy_key")
        
        # Test with multiple properties
        item = {"company_name": "Test GmbH", "city": "Berlin", "country": "Germany"}
        query_props = {"name": "company_name", "location": "city"}
        q_string = client._build_q_string(item, query_props)
        assert q_string == "Test GmbH Berlin"
        
        # Test with missing properties
        item = {"company_name": "Test GmbH"}
        q_string = client._build_q_string(item, query_props)
        assert q_string == "Test GmbH"
        
        # Test with empty properties
        item = {"company_name": "", "city": ""}
        q_string = client._build_q_string(item, query_props)
        assert q_string == ""

        # Test with None values
        item = {"company_name": None, "city": "Berlin"}
        q_string = client._build_q_string(item, query_props)
        assert q_string == "Berlin"

    def test_build_key(self):
        """Test building unique keys for items."""
        client = Handelsregister(api_key="dummy_key")
        
        # Test with defined properties
        item = {"company_name": "Test GmbH", "city": "Berlin", "id": "123"}
        query_props = {"name": "company_name", "location": "city"}
        key = client._build_key(item, query_props)
        assert key == ("Test GmbH", "Berlin")
        
        # Test with empty query properties
        key = client._build_key(item, {})
        assert isinstance(key, int)  # Should be an id(item)

    def test_merge_data(self):
        """Test merging snapshot data with file data."""
        client = Handelsregister(api_key="dummy_key")
        
        # Create sample data
        snapshot_data = [
            {"company_name": "Old GmbH", "city": "Berlin", "_handelsregister_result": {"old": "data"}},
            {"company_name": "Updated GmbH", "city": "Munich", "_handelsregister_result": {"existing": "data"}}
        ]
        
        file_data = [
            {"company_name": "Updated GmbH", "city": "Munich", "new_field": "new_value"},
            {"company_name": "New GmbH", "city": "Hamburg"}
        ]
        
        query_props = {"name": "company_name", "location": "city"}
        
        # Merge the data
        merged = client._merge_data(snapshot_data, file_data, query_props)
        
        # Verify results
        assert len(merged) == 3  # All 3 unique items (Old, Updated, New)
        
        # The old item should be marked as not in file but kept
        old_item = next(item for item in merged if item["company_name"] == "Old GmbH")
        assert old_item["_in_file"] is False
        assert "_handelsregister_result" in old_item
        
        # The updated item should be the new version but keep the old enrichment data
        updated_item = next(item for item in merged if item["company_name"] == "Updated GmbH")
        assert updated_item["_in_file"] is True
        assert "new_field" in updated_item
        assert updated_item["_handelsregister_result"] == {"existing": "data"}
        
        # The new item should be present and marked as in file
        new_item = next(item for item in merged if item["company_name"] == "New GmbH")
        assert new_item["_in_file"] is True
        assert "_handelsregister_result" not in new_item


class TestAdditionalFeatures:
    def test_fetch_dataframe(self, mock_client, sample_organization_response):
        client, _ = mock_client
        df = client.fetch_organization_df(q="OroraTech GmbH")
        assert not df.empty
        assert df.loc[0, "name"] == sample_organization_response["name"]

    def test_enrich_dataframe(self, mock_client):
        client, _ = mock_client
        import pandas as pd
        df = pd.DataFrame([
            {"company_name": "A", "city": "X"},
            {"company_name": "B", "city": "Y"},
        ])
        result = client.enrich_dataframe(
            df,
            query_properties={"name": "company_name", "location": "city"},
        )
        assert "_handelsregister_result" in result.columns
        assert len(result) == 2

    def test_cli_fetch(self, monkeypatch):
        from handelsregister.cli import main as cli_main

        called = {}

        def fake_fetch(self, q, features=None, ai_search=None):
            called['q'] = q
            called['features'] = features
            called['ai_search'] = ai_search
            return {"ok": True}

        monkeypatch.setattr("handelsregister.client.Handelsregister.fetch_organization", fake_fetch)
        monkeypatch.setenv("HANDELSREGISTER_API_KEY", "x")
        monkeypatch.setattr(
            sys,
            'argv',
            ["prog", "fetch", "ACME", "--feature", "f1", "--ai-search", "on-default"],
        )
        cli_main()
        assert called['q'] == "ACME"
        assert called['features'] == ["f1"]
        assert called['ai_search'] == "on-default"

    def test_cli_enrich(self, monkeypatch, sample_csv_file):
        from handelsregister.cli import main as cli_main

        called = {}

        def fake_enrich(self, file_path, input_type="json", **kwargs):
            called['file_path'] = file_path
            called['input_type'] = input_type
            called['params'] = kwargs.get('params')
            called['output_type'] = kwargs.get('output_type')

        monkeypatch.setattr("handelsregister.client.Handelsregister.enrich", fake_enrich)
        monkeypatch.setenv("HANDELSREGISTER_API_KEY", "x")
        monkeypatch.setattr(
            sys,
            'argv',
            [
                "prog",
                "enrich",
                sample_csv_file,
                "--input",
                "csv",
                "--feature",
                "f1",
                "--ai-search",
                "on-default",
                "--output-format",
                "csv",
            ],
        )
        cli_main()
        assert called['file_path'] == sample_csv_file
        assert called['input_type'] == "csv"
        assert called['params']['features'] == ["f1"]
        assert called['params']['ai_search'] == "on-default"
        assert called['output_type'] == "csv"

    def test_caching(self, mock_client):
        client, _ = mock_client
        client.fetch_organization(q="A")
        client.fetch_organization(q="A")
        # Only one actual HTTP call due to caching
        assert _.return_value.__enter__.return_value.get.call_count == 1

    def test_rate_limit(self, sample_organization_response):
        with patch("handelsregister.client.httpx.Client") as mock_httpx, \
             patch("handelsregister.client.time") as mock_time:
            mock_time.time.side_effect = [0, 0, 0, 0, 1, 1]
            mock_time.sleep.return_value = None
            mock_response = MagicMock()
            mock_response.json.return_value = sample_organization_response
            mock_response.raise_for_status.return_value = None
            mock_session = MagicMock()
            mock_session.get.return_value = mock_response
            mock_httpx.return_value.__enter__.return_value = mock_session

            client = Handelsregister(api_key="x", rate_limit=1)
            client.fetch_organization(q="A")
            client.fetch_organization(q="B")
            mock_time.sleep.assert_called()


class TestFetchDocument:
    def test_fetch_document_basic(self, mock_client):
        """Test basic fetch_document call."""
        client, mock_httpx = mock_client
        
        # Configure mock response for PDF
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/pdf"}
        mock_response.content = b"PDF content here"
        mock_response.raise_for_status.return_value = None
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_httpx.return_value.__enter__.return_value = mock_session
        
        # Call the method
        result = client.fetch_document(
            company_id="test_entity_id",
            document_type="shareholders_list"
        )
        
        # Verify results
        assert result == b"PDF content here"
        mock_session.get.assert_called_once()
        
        # Check that parameters were passed correctly
        args, kwargs = mock_session.get.call_args
        assert kwargs["params"]["company_id"] == "test_entity_id"
        assert kwargs["params"]["document_type"] == "shareholders_list"
        assert kwargs["params"]["api_key"] == client.api_key

    def test_fetch_document_with_output_file(self, mock_client, tmp_path):
        """Test fetch_document with output file."""
        client, mock_httpx = mock_client
        output_file = tmp_path / "test_document.pdf"
        
        # Configure mock response for PDF
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/pdf"}
        mock_response.content = b"PDF content here"
        mock_response.raise_for_status.return_value = None
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_httpx.return_value.__enter__.return_value = mock_session
        
        # Call the method with output file
        result = client.fetch_document(
            company_id="test_entity_id",
            document_type="AD",
            output_file=str(output_file)
        )
        
        # Verify file was written
        assert output_file.exists()
        assert output_file.read_bytes() == b"PDF content here"
        assert result == b"PDF content here"

    def test_fetch_document_invalid_parameters(self, mock_client):
        """Test fetch_document with invalid parameters."""
        client, _ = mock_client
        
        # Test missing company_id
        with pytest.raises(ValueError, match="Parameter 'company_id' is required"):
            client.fetch_document(company_id="", document_type="AD")
        
        # Test missing document_type
        with pytest.raises(ValueError, match="Parameter 'document_type' is required"):
            client.fetch_document(company_id="test_id", document_type="")
        
        # Test invalid document_type
        with pytest.raises(ValueError, match="Invalid document_type"):
            client.fetch_document(company_id="test_id", document_type="invalid_type")

    def test_fetch_document_error_response(self, mock_client):
        """Test handling of error responses from the document endpoint."""
        client, mock_httpx = mock_client
        
        # Configure mock response for error (JSON instead of PDF)
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"error": "Document not found"}
        mock_response.raise_for_status.return_value = None
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_httpx.return_value.__enter__.return_value = mock_session
        
        # Call the method and expect HandelsregisterError
        with pytest.raises(HandelsregisterError, match="API error: Document not found"):
            client.fetch_document(
                company_id="test_entity_id",
                document_type="CD"
            )

    def test_fetch_document_non_json_error(self, mock_client):
        """Test handling of non-JSON error responses."""
        client, mock_httpx = mock_client
        
        # Configure mock response with neither PDF nor JSON
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/html"}
        mock_response.json.side_effect = ValueError("Not JSON")
        mock_response.raise_for_status.return_value = None
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_httpx.return_value.__enter__.return_value = mock_session
        
        # Call the method and expect InvalidResponseError
        with pytest.raises(InvalidResponseError, match="Expected PDF response but got text/html"):
            client.fetch_document(
                company_id="test_entity_id",
                document_type="shareholders_list"
            )
