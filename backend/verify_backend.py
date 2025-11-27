import urllib.request
import urllib.error
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def request(method, endpoint, data=None, token=None, content_type="application/json"):
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    if data:
        if content_type == "application/json":
            body = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif content_type == "application/x-www-form-urlencoded":
            body = urllib.parse.urlencode(data).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"
    else:
        body = None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return response.status, json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))
    except Exception as e:
        print(f"Error: {e}")
        return 500, str(e)

def run_tests():
    print("Starting Verification...")
    timestamp = int(time.time())
    
    # 1. Register Team Leader
    tl_email = f"tl_{timestamp}@test.com"
    print(f"\n1. Registering Team Leader ({tl_email})...")
    status, res = request("POST", "/auth/register", {
        "name": "Test TL",
        "email": tl_email,
        "password": "password123",
        "department": "Engineering",
        "role": "team_leader"
    })
    print(f"Status: {status}, Response: {res}")
    if status != 201: print("FAILED"); return

    # 2. Register Employee
    emp_email = f"emp_{timestamp}@test.com"
    print(f"\n2. Registering Employee ({emp_email})...")
    status, res = request("POST", "/auth/register", {
        "name": "Test Emp",
        "email": emp_email,
        "password": "password123",
        "department": "Engineering",
        "role": "employee"
    })
    print(f"Status: {status}, Response: {res}")
    if status != 201: print("FAILED"); return
    emp_id = res.get("id") or res.get("_id")

    # 3. Login TL
    print(f"\n3. Logging in Team Leader...")
    status, res = request("POST", "/auth/token", {
        "username": tl_email,
        "password": "password123"
    }, content_type="application/x-www-form-urlencoded")
    print(f"Status: {status}")
    if status != 200: print("FAILED"); return
    tl_token = res["access_token"]

    # 4. Login Employee
    print(f"\n4. Logging in Employee...")
    status, res = request("POST", "/auth/token", {
        "username": emp_email,
        "password": "password123"
    }, content_type="application/x-www-form-urlencoded")
    print(f"Status: {status}")
    if status != 200: print("FAILED"); return
    emp_token = res["access_token"]

    # 5. TL Create Task
    print(f"\n5. TL Creating Task...")
    status, res = request("POST", f"/tasks/?owner_id={emp_id}", {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "high",
        "status": "pending"
    }, token=tl_token)
    print(f"Status: {status}, Response: {res}")
    if status != 201: print("FAILED"); return
    task_id = res["id"]

    # 6. Employee Try Create Task (Should Fail)
    print(f"\n6. Employee Try Create Task (Expect 403)...")
    status, res = request("POST", "/tasks/", {
        "title": "Emp Task",
        "description": "Should fail",
        "priority": "low",
        "status": "pending"
    }, token=emp_token)
    print(f"Status: {status}")
    if status != 403: print(f"FAILED (Expected 403, got {status})"); return

    # 7. Employee Get Tasks (Should be empty or own)
    print(f"\n7. Employee Get Tasks...")
    status, res = request("GET", "/tasks/mine", token=emp_token)
    print(f"Status: {status}, Count: {len(res)}")
    if status != 200: print("FAILED"); return

    # 8. TL Get All Tasks
    print(f"\n8. TL Get All Tasks...")
    status, res = request("GET", "/tasks/", token=tl_token)
    print(f"Status: {status}, Count: {len(res)}")
    if status != 200: print("FAILED"); return

    # 9. Employee Create Change Request
    print(f"\n9. Employee Create Change Request...")
    status, res = request("POST", "/requests/", {
        "field_name": "department",
        "new_value": "Marketing",
        "reason": "Transfer"
    }, token=emp_token)
    print(f"Status: {status}, Response: {res}")
    if status != 201: print("FAILED"); return
    req_id = res["id"]

    # 10. Employee Get Own Requests
    print(f"\n10. Employee Get Own Requests...")
    status, res = request("GET", "/requests/mine", token=emp_token)
    print(f"Status: {status}, Count: {len(res)}")
    if status != 200: print("FAILED"); return

    # 11. TL Get All Requests
    print(f"\n11. TL Get All Requests...")
    status, res = request("GET", "/requests/", token=tl_token)
    print(f"Status: {status}, Count: {len(res)}")
    if status != 200: print("FAILED"); return

    # 12. TL Update Task
    print(f"\n12. TL Update Task...")
    status, res = request("PUT", f"/tasks/{task_id}", {
        "title": "Updated Task Title",
        "description": "Updated description",
        "priority": "medium",
        "status": "in_progress"
    }, token=tl_token)
    print(f"Status: {status}, Response: {res}")
    if status != 200: print("FAILED"); return

    print("\nVERIFICATION SUCCESSFUL!")

if __name__ == "__main__":
    run_tests()
