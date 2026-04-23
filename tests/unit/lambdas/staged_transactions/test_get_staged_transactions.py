import json
from unittest.mock import MagicMock
import pytest

from lib.lambdas.staged_transactions.get_staged_transactions import get_staged_transactions

@pytest.fixture
def mock_mysql_interface():
    return MagicMock()

@pytest.fixture
def mock_logger():
    return MagicMock()

def test_get_staged_transactions_success(mock_mysql_interface, mock_logger):
    # Arrange
    mock_records = [
        {'id': 1, 'target_table': 'events', 'status': 'pending-review'},
        {'id': 2, 'target_table': 'events', 'status': 'pending-review'}
    ]
    mock_mysql_interface.get_staged_transactions.return_value = mock_records
    
    # Act
    response = get_staged_transactions(mock_mysql_interface, mock_logger, 'events')
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['count'] == 2
    assert body['transactions'] == mock_records
    mock_mysql_interface.get_staged_transactions.assert_called_once_with('events')
    mock_logger.error.assert_not_called()

def test_get_staged_transactions_exception(mock_mysql_interface, mock_logger):
    # Arrange
    error_message = "Database connection failed"
    mock_mysql_interface.get_staged_transactions.side_effect = Exception(error_message)
    
    # Act
    response = get_staged_transactions(mock_mysql_interface, mock_logger, 'events')
    
    # Assert
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert body['error'] == 'Internal Server Error'
    assert body['details'] == error_message
    mock_logger.error.assert_called_once()
    assert error_message in mock_logger.error.call_args[0][0]
