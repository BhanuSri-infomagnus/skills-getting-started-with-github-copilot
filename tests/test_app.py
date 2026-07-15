import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities_state():
	"""Keep tests isolated by restoring in-memory data after each test."""
	snapshot = copy.deepcopy(activities)
	yield
	activities.clear()
	activities.update(snapshot)


def test_get_activities_returns_all_activities():
	# Arrange

	# Act
	response = client.get("/activities")

	# Assert
	assert response.status_code == 200
	data = response.json()
	assert isinstance(data, dict)
	assert "Chess Club" in data


def test_signup_adds_participant():
	# Arrange
	email = "newstudent@mergington.edu"

	# Act
	response = client.post("/activities/Chess Club/signup", params={"email": email})

	# Assert
	assert response.status_code == 200
	assert response.json()["message"] == f"Signed up {email} for Chess Club"
	assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
	# Arrange
	existing_email = activities["Chess Club"]["participants"][0]

	# Act
	response = client.post("/activities/Chess Club/signup", params={"email": existing_email})

	# Assert
	assert response.status_code == 400
	assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_unknown_activity_returns_404():
	# Arrange
	email = "student@mergington.edu"

	# Act
	response = client.post("/activities/Unknown Activity/signup", params={"email": email})

	# Assert
	assert response.status_code == 404
	assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant():
	# Arrange
	email = activities["Chess Club"]["participants"][0]

	# Act
	response = client.delete(f"/activities/Chess Club/participants/{quote(email, safe='')}")

	# Assert
	assert response.status_code == 200
	assert response.json()["message"] == f"Unregistered {email} from Chess Club"
	assert email not in activities["Chess Club"]["participants"]


def test_unregister_unknown_activity_returns_404():
	# Arrange
	email = "someone@mergington.edu"

	# Act
	response = client.delete(f"/activities/Unknown Activity/participants/{quote(email, safe='')}")

	# Assert
	assert response.status_code == 404
	assert response.json()["detail"] == "Activity not found"


def test_unregister_missing_participant_returns_404():
	# Arrange
	email = "not-signed-up@mergington.edu"

	# Act
	response = client.delete(f"/activities/Chess Club/participants/{quote(email, safe='')}")

	# Assert
	assert response.status_code == 404
	assert response.json()["detail"] == "Student is not signed up for this activity"
