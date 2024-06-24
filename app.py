from flask import Flask, request, jsonify
from weaviate.exceptions import UnexpectedStatusCodeException, ObjectAlreadyExistsException
from weaviate import Client
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class WeaviateSearchAPI:
    def __init__(self, host='https://weaviate.apps.6667fbca59a2e3001e2353d0.cloud.techzone.ibm.com'):
        self.client = Client(host)

    def search(self, search_string):
        try:
            # Search for the entities based on the search string
            response = (
                self.client.query
                .get("Asset", ["assetId", "title", "description", "author"])
                .with_limit(5)
                .with_near_text({
                    "concepts": [search_string]
                })
                .with_additional(["distance"])
                .do()
            )

            # Extract relevant information from the response
            return response["data"]["Get"]["Asset"]

        except (UnexpectedStatusCodeException, ObjectAlreadyExistsException) as e:
            # Handle exceptions
            print(f"Error: {e}")
            return None

# Initialize the WeaviateSearchAPI
weaviate_api = WeaviateSearchAPI()

# API endpoint for search
@app.route('/search', methods=['GET'])
def search():
    search_string = request.args.get('q')

    if search_string:
        # Perform the search
        search_result = weaviate_api.search(search_string)

        if search_result:
            return jsonify(search_result), 200
        else:
            return jsonify({"message": "No result found or an error occurred."}), 500
    else:
        return jsonify({"message": "Please provide a search query."}), 400

if __name__ == '__main__':
    app.run(port=8081, debug=True)
