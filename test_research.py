"""
Test script for the /api/research endpoint.
Run this after starting the server with: uvicorn app.main:app --reload
"""

import requests
import json


def test_research_endpoint():
    url = "http://localhost:8000/api/research"

    # Example request payload
    payload = {
        "problem_statement": "People struggle to find healthy meal options when working from home",
        "target_users": "Remote workers"
    }

    print("=" * 60)
    print("Testing ResearchAI /api/research endpoint")
    print("=" * 60)
    print(f"\nProblem Statement: {payload['problem_statement']}")
    print(f"Target Users: {payload['target_users']}")
    print("\nSending request to API...")
    print("-" * 60)

    try:
        response = requests.post(url, json=payload, timeout=120)

        if response.status_code == 200:
            data = response.json()

            print(f"\n✓ SUCCESS!")
            print(f"\nPosts Analyzed: {data['total_posts_analyzed']}")
            print(f"Comments Analyzed: {data['total_comments_analyzed']}")
            print(f"Pain Points Found: {len(data['pain_points'])}")
            print("\n" + "=" * 60)
            print("PAIN POINTS:")
            print("=" * 60)

            for idx, pain_point in enumerate(data['pain_points'], 1):
                print(f"\n{idx}. {pain_point['description']}")
                print(f"   Severity: {pain_point['severity']}")
                print(f"   Quote: \"{pain_point['quote'][:100]}...\"")
                print(f"   Source: {pain_point['source_url']}")
                print(f"   Frequency: {pain_point['frequency']}")

            # Save full response to file
            with open('research_results.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n\nFull results saved to: research_results.json")

        else:
            print(f"\n✗ ERROR: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.Timeout:
        print("\n✗ ERROR: Request timed out (>120s)")
        print("The API may be processing a large amount of data.")
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to the API")
        print("Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")


if __name__ == "__main__":
    test_research_endpoint()
