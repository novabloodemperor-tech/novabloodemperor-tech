import requests
import json

# Test data - a student with good grades
test_data = {
    "cluster_points": 42.0,
    "grades": {
        "Mathematics": "B+",
        "English": "B",
        "Physics": "B-",
        "Chemistry": "C+"
    }
}

try:
    # Send POST request to your LIVE API (not localhost)
    response = requests.post(
        'https://novabloodemperor-tech-backend.onrender.com/api/check-eligibility/',
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print("Status Code:", response.status_code)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS! API is working with real KUCCPS data!")
        print(f"🎯 Found {data.get('total_found', 0)} eligible courses")
        
        # Show courses
        programmes = data.get('eligible_programmes', [])
        for i, programme in enumerate(programmes[:5]):  # Show first 5
            print(f"   {i+1}. {programme.get('programme_name')}")
            print(f"      🏛️  {programme.get('university')}")
            print(f"      📊 {programme.get('cluster_points')} points")
            print()
        
        if len(programmes) > 5:
            print(f"   ... and {len(programmes) - 5} more courses")
    else:
        print("❌ Error:", response.status_code)
        print("Response:", response.text)
        
except Exception as e:
    print("❌ API Test Failed:", e)