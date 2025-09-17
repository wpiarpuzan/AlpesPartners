.PHONY: postman

postman:
	newman run postman/entrega5-saga.postman_collection.json -e postman/env.json
