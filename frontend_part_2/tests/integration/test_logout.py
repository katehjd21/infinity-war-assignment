def test_logout_clears_session(mock_api_session_post, logged_in_authenticated_user):
    mock_api_session_post("app", {"message": "Logged out"})

    client = logged_in_authenticated_user
    response = client.post("/logout?testing=1", follow_redirects=True)
    html = response.data.decode()

    with client.session_transaction() as session:
        assert session.get("username") is None
        assert session.get("role") is None

    assert "Login" in html
    assert "You have been logged out." in html