import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database_setup.db_manager import get_db_connection, save_player

class TestDatabaseIntegration(unittest.TestCase):

    def setUp(self):
        self.test_ids = ["verify-123", "dup-999"]
        print("\n" + "="*60)
        print(f"STARTING TEST: {self._testMethodName}")
        print("-" * 60)

    def tearDown(self):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            for tid in self.test_ids:
                cursor.execute("DELETE FROM PLAYER WHERE summoner_id = %s", (tid,))
            conn.commit()
            cursor.close()
            conn.close()
            print("CLEANUP: Database scrubbed of test records.")
        print("="*60 + "\n")

    def test_1_auth_handshake(self):
        """[Security] Verify MySQL Handshake"""
        print("ACTION: Testing connection to 127.0.0.1...")
        conn = get_db_connection()
        
        # Output connection details
        if conn and conn.is_connected():
            db_info = conn.get_server_info()
            print(f"OBSERVATION: Connected to MySQL Server version {db_info}")
            print("RESULT: Handshake successful.")
        
        self.assertIsNotNone(conn)
        if conn: conn.close()

    def test_2_state_verification(self):
        """[Integration] Verify PLAYER Data Persistence"""
        print("ACTION: Executing save_player('verify-123', 'TestUser')...")
        save_player("verify-123", "TestUser")
        
        print("ACTION: Querying database for newly inserted record...")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) # dictionary=True makes output readable
        cursor.execute("SELECT * FROM PLAYER WHERE summoner_id = 'verify-123'")
        result = cursor.fetchone()
        
        # Show exactly what is in the DB
        print(f"OBSERVATION: Database returned row: {result}")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['summoner_name'], "TestUser")
        print("RESULT: Persistence verified. Data matches input.")
        cursor.close()
        conn.close()

    def test_3_conflict_handling(self):
        """[Data Integrity] Verify Duplicate Entry Protection"""
        print("ACTION: Inserting original record ('dup-999', 'Original')...")
        save_player("dup-999", "Original")
        
        print("ACTION: Attempting to overwrite with ('dup-999', 'Clone')...")
        save_player("dup-999", "Clone")
        
        # Retrieve to see which one "won"
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM PLAYER WHERE summoner_id = 'dup-999'")
        result = cursor.fetchone()
        
        print(f"OBSERVATION: Current record in DB: {result}")
        
        # If INSERT IGNORE is working, it should still be "Original"
        self.assertEqual(result['summoner_name'], "Original")
        print("RESULT: Duplicate ignored. Data integrity maintained.")
        cursor.close()
        conn.close()

if __name__ == "__main__":
    unittest.main(verbosity=1)