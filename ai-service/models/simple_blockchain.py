"""
Simple Blockchain Implementation for FRA Atlas
Uses hash-based proof-of-work for tamper-proof records
"""

import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class BlockData:
    """Data stored in a block"""
    transaction_id: str
    transaction_type: str  # 'claim_submission', 'approval', 'rejection', 'document_upload'
    data: Dict[str, Any]
    timestamp: str
    user_id: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class Block:
    """Individual block in the blockchain"""
    index: int
    timestamp: str
    data: BlockData
    previous_hash: str
    hash: str
    nonce: int = 0
    
    def to_dict(self) -> Dict:
        """Convert block to dictionary"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': asdict(self.data),
            'previous_hash': self.previous_hash,
            'hash': self.hash,
            'nonce': self.nonce
        }


class SimpleBlockchain:
    """
    Simple blockchain implementation for FRA Atlas
    Provides tamper-proof storage of critical transactions
    """
    
    def __init__(self, difficulty: int = 4):
        """
        Initialize blockchain
        
        Args:
            difficulty: Number of leading zeros required in hash (mining difficulty)
        """
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions: List[BlockData] = []
        
        # Create genesis block
        self.create_genesis_block()
        
        logger.info(f"✅ Blockchain initialized (difficulty: {difficulty})")
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_data = BlockData(
            transaction_id="GENESIS",
            transaction_type="genesis",
            data={"message": "FRA Atlas Blockchain - Genesis Block"},
            timestamp=datetime.now().isoformat()
        )
        
        genesis_block = Block(
            index=0,
            timestamp=datetime.now().isoformat(),
            data=genesis_data,
            previous_hash="0",
            hash="",
            nonce=0
        )
        
        # Mine the genesis block
        genesis_block.hash = self.calculate_hash(genesis_block)
        self.chain.append(genesis_block)
        
        logger.info("🔗 Genesis block created")
    
    def calculate_hash(self, block: Block) -> str:
        """
        Calculate SHA-256 hash of block
        
        Args:
            block: Block to hash
            
        Returns:
            Hexadecimal hash string
        """
        block_string = json.dumps({
            'index': block.index,
            'timestamp': block.timestamp,
            'data': asdict(block.data),
            'previous_hash': block.previous_hash,
            'nonce': block.nonce
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, block: Block) -> Block:
        """
        Mine block using proof-of-work
        
        Args:
            block: Block to mine
            
        Returns:
            Mined block with valid hash
        """
        target = "0" * self.difficulty
        
        logger.info(f"⛏️ Mining block {block.index}...")
        start_time = time.time()
        
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = self.calculate_hash(block)
        
        mining_time = time.time() - start_time
        logger.info(f"✅ Block {block.index} mined in {mining_time:.2f}s (nonce: {block.nonce})")
        
        return block
    
    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain"""
        return self.chain[-1]
    
    def add_transaction(self, transaction_data: BlockData) -> str:
        """
        Add transaction to pending transactions
        
        Args:
            transaction_data: Transaction data to add
            
        Returns:
            Transaction ID
        """
        self.pending_transactions.append(transaction_data)
        logger.info(f"📝 Transaction added: {transaction_data.transaction_id}")
        return transaction_data.transaction_id
    
    def mine_pending_transactions(self) -> Optional[Block]:
        """
        Mine all pending transactions into a new block
        
        Returns:
            Newly mined block or None if no pending transactions
        """
        if not self.pending_transactions:
            logger.warning("No pending transactions to mine")
            return None
        
        # For simplicity, mine one transaction at a time
        transaction_data = self.pending_transactions.pop(0)
        
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now().isoformat(),
            data=transaction_data,
            previous_hash=self.get_latest_block().hash,
            hash="",
            nonce=0
        )
        
        # Mine the block
        mined_block = self.mine_block(new_block)
        self.chain.append(mined_block)
        
        logger.info(f"🔗 Block added to chain (height: {len(self.chain)})")
        return mined_block
    
    def add_block_direct(self, transaction_data: BlockData) -> Block:
        """
        Add and mine a block immediately (convenience method)
        
        Args:
            transaction_data: Transaction data
            
        Returns:
            Mined block
        """
        self.add_transaction(transaction_data)
        return self.mine_pending_transactions()
    
    def is_chain_valid(self) -> bool:
        """
        Validate the entire blockchain
        
        Returns:
            True if chain is valid, False otherwise
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current hash is correct
            if current_block.hash != self.calculate_hash(current_block):
                logger.error(f"❌ Invalid hash at block {i}")
                return False
            
            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                logger.error(f"❌ Invalid previous hash at block {i}")
                return False
            
            # Check proof-of-work
            if not current_block.hash.startswith("0" * self.difficulty):
                logger.error(f"❌ Invalid proof-of-work at block {i}")
                return False
        
        logger.info("✅ Blockchain is valid")
        return True
    
    def get_block_by_index(self, index: int) -> Optional[Block]:
        """Get block by index"""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None
    
    def get_block_by_transaction_id(self, transaction_id: str) -> Optional[Block]:
        """Find block containing specific transaction"""
        for block in self.chain:
            if block.data.transaction_id == transaction_id:
                return block
        return None
    
    def get_transaction_proof(self, transaction_id: str) -> Optional[Dict]:
        """
        Get cryptographic proof for a transaction
        
        Args:
            transaction_id: Transaction to prove
            
        Returns:
            Proof dictionary or None
        """
        block = self.get_block_by_transaction_id(transaction_id)
        if not block:
            return None
        
        return {
            'transaction_id': transaction_id,
            'block_index': block.index,
            'block_hash': block.hash,
            'previous_block_hash': block.previous_hash,
            'timestamp': block.timestamp,
            'nonce': block.nonce,
            'verified': self.is_chain_valid(),
            'chain_height': len(self.chain),
            'verification_url': f"/api/blockchain/verify/{transaction_id}"
        }
    
    def export_chain(self) -> List[Dict]:
        """Export entire blockchain as JSON-serializable list"""
        return [block.to_dict() for block in self.chain]
    
    def get_chain_stats(self) -> Dict:
        """Get blockchain statistics"""
        return {
            'total_blocks': len(self.chain),
            'difficulty': self.difficulty,
            'pending_transactions': len(self.pending_transactions),
            'is_valid': self.is_chain_valid(),
            'genesis_timestamp': self.chain[0].timestamp if self.chain else None,
            'latest_block_timestamp': self.chain[-1].timestamp if self.chain else None,
            'latest_block_hash': self.chain[-1].hash if self.chain else None
        }


# Global blockchain instance
_blockchain_instance: Optional[SimpleBlockchain] = None


def get_blockchain() -> SimpleBlockchain:
    """Get or create singleton blockchain instance"""
    global _blockchain_instance
    if _blockchain_instance is None:
        _blockchain_instance = SimpleBlockchain(difficulty=4)
    return _blockchain_instance


def record_claim_submission(claim_id: str, claim_data: Dict) -> Dict:
    """
    Record a claim submission on blockchain
    
    Args:
        claim_id: Unique claim identifier
        claim_data: Claim details
        
    Returns:
        Blockchain proof
    """
    blockchain = get_blockchain()
    
    transaction_data = BlockData(
        transaction_id=f"CLAIM-{claim_id}",
        transaction_type="claim_submission",
        data={
            'claim_id': claim_id,
            'village_name': claim_data.get('village_name'),
            'applicant_name': claim_data.get('applicant_name'),
            'area_hectares': claim_data.get('area_hectares'),
            'submitted_at': datetime.now().isoformat()
        },
        timestamp=datetime.now().isoformat(),
        user_id=claim_data.get('user_id'),
        metadata={'ip_address': claim_data.get('ip_address')}
    )
    
    block = blockchain.add_block_direct(transaction_data)
    return blockchain.get_transaction_proof(transaction_data.transaction_id)


def record_approval(claim_id: str, approval_data: Dict) -> Dict:
    """Record claim approval on blockchain"""
    blockchain = get_blockchain()
    
    transaction_data = BlockData(
        transaction_id=f"APPROVAL-{claim_id}",
        transaction_type="approval",
        data={
            'claim_id': claim_id,
            'approved_by': approval_data.get('approved_by'),
            'approval_date': datetime.now().isoformat(),
            'patta_number': approval_data.get('patta_number')
        },
        timestamp=datetime.now().isoformat(),
        user_id=approval_data.get('user_id')
    )
    
    block = blockchain.add_block_direct(transaction_data)
    return blockchain.get_transaction_proof(transaction_data.transaction_id)


def verify_transaction(transaction_id: str) -> Dict:
    """
    Verify a transaction exists on blockchain
    
    Args:
        transaction_id: Transaction to verify
        
    Returns:
        Verification result
    """
    blockchain = get_blockchain()
    proof = blockchain.get_transaction_proof(transaction_id)
    
    if not proof:
        return {
            'verified': False,
            'message': 'Transaction not found on blockchain'
        }
    
    return {
        'verified': True,
        'message': 'Transaction verified on blockchain',
        'proof': proof
    }


if __name__ == "__main__":
    # Test the blockchain
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Simple Blockchain Test")
    print("=" * 60)
    
    # Create blockchain
    blockchain = get_blockchain()
    
    # Add test transactions
    print("\n[1/3] Adding test transactions...")
    proof1 = record_claim_submission("TEST-001", {
        'village_name': 'Kheda',
        'applicant_name': 'Test User',
        'area_hectares': 10.5,
        'user_id': 'user123'
    })
    
    proof2 = record_approval("TEST-001", {
        'approved_by': 'Forest Officer',
        'patta_number': 'MH/GDC/2024/TEST-001',
        'user_id': 'officer456'
    })
    
    print(f"\n[2/3] Verifying transactions...")
    verification = verify_transaction("CLAIM-TEST-001")
    print(f"Verification result: {verification['verified']}")
    
    print(f"\n[3/3] Chain statistics...")
    stats = blockchain.get_chain_stats()
    print(json.dumps(stats, indent=2))
    
    print("\n" + "=" * 60)
    print("✅ Blockchain test complete!")
    print("=" * 60)
