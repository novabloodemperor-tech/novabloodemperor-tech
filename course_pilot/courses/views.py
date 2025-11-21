from rest_framework.decorators import api_view
from rest_framework.response import Response
import csv
import os

# Load all programmes from CSV file
def load_all_programmes():
    programmes = []
    csv_file = "data/cleaned/KUCCPS_ClusterPoints_Cleaned.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return programmes
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            
            for row_num, row in enumerate(reader, start=2):
                if len(row) >= 5 and row[1] and row[3]:  # Check if has programme code and name
                    try:
                        programme_code = row[1].strip()
                        programme_name = row[3].strip()
                        university = row[2].strip()
                        
                        # Convert cluster points to float
                        cluster_points_str = row[4].strip()
                        if cluster_points_str and cluster_points_str != '-':
                            cluster_points = float(cluster_points_str)
                        else:
                            cluster_points = 0.0
                        
                        programmes.append({
                            'programme_code': programme_code,
                            'programme_name': programme_name,
                            'university': university,
                            'cluster_points': cluster_points
                        })
                        
                    except Exception as e:
                        print(f⚠️ Skipping row {row_num}: {e}")
                        continue
        
        print(f"✅ Loaded {len(programmes)} programmes from CSV")
        return programmes
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return programmes

# Load programmes once when the server starts
ALL_PROGRAMMES = load_all_programmes()

@api_view(['POST'])
def check_eligibility(request):
    try:
        data = request.data
        user_cluster_points = float(data.get('cluster_points', 0))
        
        print(f"🔍 Checking eligibility with {len(ALL_PROGRAMMES)} programmes")
        print(f"📊 User cluster points: {user_cluster_points}")
        
        # Filter programmes by cluster points
        eligible_programmes = []
        for programme in ALL_PROGRAMMES:
            if user_cluster_points >= programme['cluster_points']:
                eligible_programmes.append({
                    'programme_code': programme['programme_code'],
                    'programme_name': programme['programme_name'],
                    'university': programme['university'],
                    'cluster_points': programme['cluster_points'],
                    'required_cluster': programme['cluster_points']
                })
        
        print(f"🎯 Found {len(eligible_programmes)} eligible programmes")
        
        return Response({
            'eligible_programmes': eligible_programmes,
            'total_found': len(eligible_programmes),
            'database_total': len(ALL_PROGRAMMES),
            'message': f'Found {len(eligible_programmes)} courses matching your {user_cluster_points} cluster points'
        })
        
    except Exception as e:
        print(f"❌ Error in eligibility check: {e}")
        return Response({
            'eligible_programmes': [],
            'total_found': 0,
            'message': f'Error: {str(e)}'
        }, status=500)

@api_view(['GET'])
def check_database(request):
    return Response({
        'total_programmes': len(ALL_PROGRAMMES),
        'status': 'working',
        'message': f'Using CSV data with {len(ALL_PROGRAMMES)} programmes'
    })

@api_view(['POST'])
def pay(request):
    try:
        phone = request.data.get("phone")
        amount = request.data.get("amount")

        if not phone or not amount:
            return Response({"error": "Phone and amount are required"}, status=400)

        return Response({
            "success": True,
            "message": "Payment initiated successfully!",
            "phone": phone,
            "amount": amount,
            "transaction_id": "TEST_12345"
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)
