from models import CodeSubmission


def test_submit_code(client, db_session, test_user):
    body = {"code_text": "sample text"}
    
    response = client.post("/submit-code/", json=body)
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data is not None
    assert data["code_text"] == body["code_text"]
    
    code = db_session.query(CodeSubmission).filter(CodeSubmission.user_id == test_user.id).first()
    
    assert code is not None
    assert code.code_text == body["code_text"]
    assert data["ai_response"] is not None
    


def test_history(client, test_user, test_code_submission):
    response = client.get("/api/history/")
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data is not None
    assert isinstance(data, list)
    assert data[0]["id"] == test_code_submission.id



def test_single_chat(client, test_user, test_code_submission):
    response = client.get(f"/api/history/{test_code_submission.id}")
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data is not None
    assert data["id"] == test_code_submission.id
    assert data["code_text"] == test_code_submission.code_text
    

def test_wrong_single_chat(client):
    id = 999
    response = client.get(f"/api/history/{id}/")
    
    assert response.status_code == 200
    assert response.json() is None


def test_search_chat(client, test_user, test_code_submission):
    response = client.get("/search/?q=Test")
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data is not None
    assert isinstance(data, list)
    assert data[0]["id"] == test_code_submission.id
    

def test_search_not_found(client):
    response = client.get("/search/?q=random test hjbswdhjehjfdhw")
    
    assert response.status_code == 200
    assert response.json() == []


def test_delete_chat(client, test_user, test_code_submission, db_session):
    response = client.delete(f"/history/{test_code_submission.id}")
    
    assert response.status_code == 200
    
    assert response.json()["message"] == "chat deleted successfully"
    
    chat = db_session.query(CodeSubmission).filter(CodeSubmission.id == test_code_submission.id).first()
    
    assert chat is None