"""
FastAPI Activity Management Tests using AAA (Arrange-Act-Assert) Pattern

Tests for the Mergington High School Activities API endpoints including:
- GET /activities - retrieve all activities
- POST /activities/{activity_name}/signup - sign up for an activity
- DELETE /activities/{activity_name}/signup - unregister from an activity
- GET / - root redirect
"""
import pytest


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """
        Test that GET / redirects to /static/index.html
        
        AAA Pattern:
        - Arrange: Client is ready (from fixture)
        - Act: Make GET request to /
        - Assert: Verify 307 redirect status and correct location header
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for retrieving activities"""

    def test_get_all_activities_returns_success(self, client):
        """
        Test that GET /activities returns all activities with 200 status
        
        AAA Pattern:
        - Arrange: Client ready, activities initialized in fixture
        - Act: Make GET request to /activities
        - Assert: Verify 200 status and valid activity data
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_includes_all_fields(self, client):
        """
        Test that activity objects contain all required fields
        
        AAA Pattern:
        - Arrange: Client ready, activities initialized
        - Act: Get activities and extract one activity
        - Assert: Verify all required fields are present
        """
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignupForActivity:
    """Tests for signup functionality"""

    def test_signup_for_activity_success(self, client):
        """
        Test successful signup for an activity
        
        AAA Pattern:
        - Arrange: New student email that's not yet registered
        - Act: POST signup request
        - Assert: Verify 200 status and success message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """
        Test that signup actually adds participant to activity list
        
        AAA Pattern:
        - Arrange: New student email
        - Act: Signup and then fetch activities
        - Assert: Verify participant is in the activity's participant list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_student_returns_error(self, client):
        """
        Test that signing up a student who's already registered returns 400 error
        
        AAA Pattern:
        - Arrange: Email that's already registered for activity
        - Act: POST signup request with existing participant email
        - Assert: Verify 400 status and "already signed up" error message
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Test that signing up for a non-existent activity returns 404 error
        
        AAA Pattern:
        - Arrange: Fake activity name
        - Act: POST signup request for non-existent activity
        - Assert: Verify 404 status and "not found" error message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_with_special_characters_in_activity_name(self, client):
        """
        Test signup with activity names containing special characters (URL encoded)
        
        AAA Pattern:
        - Arrange: Activity name and email ready
        - Act: POST signup with URL encoding
        - Assert: Verify signup succeeds
        """
        # Arrange
        activity_name = "Chess Club"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for unregister/delete functionality"""

    def test_unregister_existing_participant_success(self, client):
        """
        Test successful unregistration of an existing participant
        
        AAA Pattern:
        - Arrange: Existing participant email
        - Act: DELETE unregister request
        - Assert: Verify 200 status and success message
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant_from_activity(self, client):
        """
        Test that unregister actually removes participant from activity list
        
        AAA Pattern:
        - Arrange: Existing participant
        - Act: Unregister and then fetch activities
        - Assert: Verify participant is removed from activity's list
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act
        client.delete(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert existing_email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        Test that unregistering from a non-existent activity returns 404 error
        
        AAA Pattern:
        - Arrange: Fake activity name
        - Act: DELETE unregister request for non-existent activity
        - Assert: Verify 404 status
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404

    def test_unregister_non_participant_returns_404(self, client):
        """
        Test that unregistering a non-participant returns 404 error
        
        AAA Pattern:
        - Arrange: Email not registered for activity
        - Act: DELETE unregister request
        - Assert: Verify 404 status and "Participant not found" message
        """
        # Arrange
        activity_name = "Chess Club"
        non_participant_email = "notmember@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={non_participant_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_unregister_then_signup_again_succeeds(self, client):
        """
        Test that after unregistering, a student can sign up again
        
        AAA Pattern:
        - Arrange: Existing participant
        - Act: Unregister, then signup again
        - Assert: Verify second signup succeeds
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act - unregister first
        client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Act - signup again
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]


class TestIntegrationScenarios:
    """Integration tests combining multiple operations"""

    def test_full_signup_and_unregister_flow(self, client):
        """
        Test complete flow: signup, verify, unregister, verify
        
        AAA Pattern:
        - Arrange: New student email and activity
        - Act: Signup, get activities, unregister, get activities again
        - Assert: Verify each step with correct participant counts
        """
        # Arrange
        activity_name = "Chess Club"
        email = "testflow@mergington.edu"
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity_name]["participants"])

        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        activities_after_signup = client.get("/activities").json()
        count_after_signup = len(
            activities_after_signup[activity_name]["participants"]
        )

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        activities_after_unregister = client.get("/activities").json()
        count_after_unregister = len(
            activities_after_unregister[activity_name]["participants"]
        )

        # Assert
        assert signup_response.status_code == 200
        assert count_after_signup == initial_count + 1
        assert unregister_response.status_code == 200
        assert count_after_unregister == initial_count
        assert email not in activities_after_unregister[activity_name]["participants"]

    def test_multiple_students_signup_same_activity(self, client):
        """
        Test that multiple students can signup for the same activity
        
        AAA Pattern:
        - Arrange: Multiple new student emails
        - Act: Each student signs up for same activity
        - Assert: Verify all students are in participant list
        """
        # Arrange
        activity_name = "Programming Class"
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu",
        ]

        # Act
        for student_email in students:
            client.post(f"/activities/{activity_name}/signup?email={student_email}")

        response = client.get("/activities")

        # Assert
        activity_participants = response.json()[activity_name]["participants"]
        for student_email in students:
            assert student_email in activity_participants
