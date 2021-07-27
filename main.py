import hashlib
import json

from time import time
from uuid import uuid4
from flask import Flask, jsonify, request


class MyBlockchain(object):
    def __init__(self):

        self.transactions = []
        self.ledger = []

        # first block
        self.create_block(previous_hash=1, proof=100)

    # make new block in chain
    def create_block(self, proof, previous_hash=None):

        block = {
            'index': len(self.ledger) + 1,
            'timestamp': time(),
            'transactions': self.transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.ledger[-1]),
        }

        # reset current list
        self.transactions = []

        self.ledger.append(block)
        return block

    # Creates a new transaction to go into the next mined Block
    def create_transaction(self, sender, recipient, amount):

        self.transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.ledger[-1]

    # Creates a SHA-256 hash of a Block
    @staticmethod
    def hash(block):

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    # leading 0 hash algo
    # do some computational work to receive a coin
    def proof_of_work(self, last_proof):

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    # checks for 0s in last proof
    # sha256 security hashing function
    @staticmethod
    def valid_proof(last_proof, proof):

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = MyBlockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # you solved the proof so you get a coin (successful mine)
    # sender is "0" to signify that this node has mined a new coin.
    blockchain.create_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/create', methods=['POST'])
def create_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.create_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/ledger', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.ledger,
        'length': len(blockchain.ledger),
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
