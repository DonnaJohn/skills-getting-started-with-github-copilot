import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert "Basketball" in activities
        assert "Tennis Club" in activities
        assert "Art Studio" in activities
        assert "Theater Club" in activities
        assert "Debate Team" in activities
        assert "Robotics Club" in activities
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_basketball_has_initial_participant(self, client):
        """Test that Basketball has alex@mergington.edu as initial participant"""
        response = client.get("/activities")
        activities = response.json()
        
        assert "alex@mergington.edu" in activities["Basketball"]["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student(self, client):
        """Test signing up a new student for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newstudent@mergington.edu" in activities["Basketball"]["participants"]

    def test_signup_duplicate_student_fails(self, client):
        """Test that signing up the same student twice fails"""
        # First signup
        client.post("/activities/Basketball/signup?email=student@mergington.edu")
        
        # Second signup attempt
        response = client.post(
            "/activities/Basketball/signup?email=student@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_to_nonexistent_activity_fails(self, client):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/NonexistentClub/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_students(self, client):
        """Test that multiple different students can sign up"""
        students = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for student in students:
            response = client.post(
                f"/activities/Tennis Club/signup?email={student}"
            )
            assert response.status_code == 200
        
        # Verify all students are added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        tennis_participants = activities["Tennis Club"]["participants"]
        
        for student in students:
            assert student in tennis_participants


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        response = client.post(
            "/activities/Basketball/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert "alex@mergington.edu" in data["message"]
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "alex@mergington.edu" not in activities["Basketball"]["participants"]

    def test_unregister_nonexistent_participant_fails(self, client):
        """Test that unregistering a non-existent participant fails"""
        response = client.post(
            "/activities/Basketball/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Test that unregistering from a non-existent activity fails"""
        response = client.post(
            "/activities/NonexistentClub/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_multiple_participants(self, client):
        """Test unregistering multiple participants from an activity"""
        # Art Studio has isabella@mergington.edu and mia@mergington.edu
        response1 = client.post(
            "/activities/Art Studio/unregister?email=isabella@mergington.edu"
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            "/activities/Art Studio/unregister?email=mia@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both were removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert len(activities["Art Studio"]["participants"]) == 0


class TestSignupAndUnregister:
    """Integration tests for signup and unregister workflows"""

    def test_signup_then_unregister(self, client):
        """Test signing up then unregistering a student"""
        student = "temp@mergington.edu"
        
        # Signup
        signup_response = client.post(
            f"/activities/Basketball/signup?email={student}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert student in activities["Basketball"]["participants"]
        
        # Unregister
        unregister_response = client.post(
            f"/activities/Basketball/unregister?email={student}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert student not in activities["Basketball"]["participants"]

    def test_signup_to_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        student = "multi@mergington.edu"
        activities_to_join = ["Basketball", "Tennis Club", "Chess Club"]
        
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup?email={student}"
            )
            assert response.status_code == 200
        
        # Verify student is in all activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        for activity in activities_to_join:
            assert student in activities[activity]["participants"]
