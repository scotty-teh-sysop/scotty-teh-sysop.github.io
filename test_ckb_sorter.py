#!/usr/bin/env python3
"""
Test script for CKB Document Sorter
"""

import os
import tempfile
import shutil
from pathlib import Path

# Import the sorter
import sys
sys.path.insert(0, str(Path(__file__).parent))

from ckb_document_sorter import (
    CKBDocumentParser, CKBDocumentSorter, CKBDocument, CKBHeader,
    Jurisdiction, PartyType, DocumentType, JUDICIAL_CENTRES,
    DOCUMENT_TYPE_PRECEDENCE, PARTY_TYPE_PRECEDENCE, JURISDICTION_PRECEDENCE
)

def test_header_parsing():
    """Test parsing of various CKB header formats"""
    
    # Test 1: Standard civil document
    civil_text = """COURT FILE NUMBER: 2303-12345
JUDICIAL CENTRE: Calgary
PLAINTIFF: John Smith
DEFENDANT: Jane Doe
DOCUMENT: Statement of Claim
ADDRESS FOR SERVICE: 123 Main Street, Calgary, AB T2P 1A1
FILED ON: January 15, 2023
CLERK'S STAMP: FILED 2023-01-15

IN THE COURT OF KING'S BENCH OF ALBERTA
JUDICIAL CENTRE OF CALGARY

BETWEEN:
JOHN SMITH
PLAINTIFF

AND:
JANE DOE
DEFENDANT

STATEMENT OF CLAIM"""
    
    doc = CKBDocumentParser.parse(civil_text, "test_civil.txt")
    h = doc.header
    
    assert h.court_file_number == "2303-12345", "Expected 2303-12345, got " + h.court_file_number
    assert h.judicial_centre == "Calgary", "Expected Calgary, got " + h.judicial_centre
    assert h.plaintiff == "John Smith", "Expected John Smith, got " + h.plaintiff
    assert h.defendant == "Jane Doe", "Expected Jane Doe, got " + h.defendant
    assert h.document_type == "Statement of Claim", "Expected Statement of Claim, got " + h.document_type
    assert h.jurisdiction == Jurisdiction.CIVIL, "Expected CIVIL, got " + str(h.jurisdiction)
    assert h.party_type == PartyType.PLAINTIFF, "Expected PLAINTIFF, got " + str(h.party_type)
    assert h.doc_type_enum == DocumentType.STATEMENT_OF_CLAIM, "Expected STATEMENT_OF_CLAIM, got " + str(h.doc_type_enum)
    assert h.year == 2023, "Expected 2023, got " + str(h.year)
    assert h.sequence == 12345, "Expected 12345, got " + str(h.sequence)
    assert h.date_id == "2023-12345", "Expected 2023-12345, got " + h.date_id
    
    print("Test 1 passed: Standard civil document parsing")
    
    # Test 2: Criminal document
    criminal_text = """COURT FILE NUMBER: 2212-09876
JUDICIAL CENTRE: Lethbridge
PROSECUTION: His Majesty the King
ACCUSED: Robert Johnson
DOCUMENT: Information
ADDRESS FOR SERVICE: Crown Prosecutor's Office, Lethbridge, AB
FILED ON: March 10, 2022
CLERK'S STAMP: FILED 2022-03-10

IN THE COURT OF KING'S BENCH OF ALBERTA
JUDICIAL CENTRE OF LETHBRIDGE

BETWEEN:
HIS MAJESTY THE KING
PROSECUTION

AND:
ROBERT JOHNSON
ACCUSED

INFORMATION"""
    
    doc2 = CKBDocumentParser.parse(criminal_text, "test_criminal.txt")
    h2 = doc2.header
    
    assert h2.prosecution == "His Majesty the King", "Expected His Majesty the King, got " + h2.prosecution
    assert h2.accused == "Robert Johnson", "Expected Robert Johnson, got " + h2.accused
    assert h2.jurisdiction == Jurisdiction.CRIMINAL, "Expected CRIMINAL, got " + str(h2.jurisdiction)
    assert h2.party_type == PartyType.PROSECUTION, "Expected PROSECUTION, got " + str(h2.party_type)
    assert h2.doc_type_enum == DocumentType.INFORMATION, "Expected INFORMATION, got " + str(h2.doc_type_enum)
    
    print("Test 2 passed: Criminal document parsing")
    
    # Test 3: Family document
    family_text = """COURT FILE NUMBER: 2405-00123
JUDICIAL CENTRE: Red Deer
PLAINTIFF: Sarah Wilson
DEFENDANT: Michael Wilson
DOCUMENT: Parenting Order
ADDRESS FOR SERVICE: 789 Gaetz Avenue, Red Deer, AB T4P 2J7
FILED ON: June 1, 2024

IN THE COURT OF KING'S BENCH OF ALBERTA
JUDICIAL CENTRE OF RED DEER
FAMILY LAW

BETWEEN:
SARAH WILSON
APPLICANT

AND:
MICHAEL WILSON
RESPONDENT

PARENTING ORDER"""
    
    doc3 = CKBDocumentParser.parse(family_text, "test_family.txt")
    h3 = doc3.header
    
    assert h3.jurisdiction == Jurisdiction.FAMILY, "Expected FAMILY, got " + str(h3.jurisdiction)
    assert h3.doc_type_enum == DocumentType.PARENTING_ORDER, "Expected PARENTING_ORDER, got " + str(h3.doc_type_enum)
    
    print("Test 3 passed: Family document parsing")
    
    # Test 4: Surrogate/Probate document
    probate_text = """COURT FILE NUMBER: 2309-04567
JUDICIAL CENTRE: Medicine Hat
PLAINTIFF: Estate of Mary Thompson
DOCUMENT: Application for Grant of Probate
ADDRESS FOR SERVICE: 321 South Railway Street, Medicine Hat, AB T1A 2B3
FILED ON: October 5, 2023

IN THE COURT OF KING'S BENCH OF ALBERTA
JUDICIAL CENTRE OF MEDICINE HAT
SURROGATE MATTERS

IN THE ESTATE OF:
MARY THOMPSON
DECEASED

APPLICATION FOR GRANT OF PROBATE"""
    
    doc4 = CKBDocumentParser.parse(probate_text, "test_probate.txt")
    h4 = doc4.header
    
    assert h4.jurisdiction == Jurisdiction.SURROGATE, "Expected SURROGATE, got " + str(h4.jurisdiction)
    
    print("Test 4 passed: Surrogate/Probate document parsing")
    
    # Test 5: Judicial centre from "IN THE COURT" line
    centre_text = """COURT FILE NUMBER: 2301-11111
PLAINTIFF: Test Plaintiff
DEFENDANT: Test Defendant
DOCUMENT: Notice

IN THE COURT OF KING'S BENCH OF ALBERTA
JUDICIAL CENTRE OF EDMONTON

BETWEEN:
TEST PLAINTIFF
PLAINTIFF

AND:
TEST DEFENDANT
DEFENDANT

NOTICE"""
    
    doc5 = CKBDocumentParser.parse(centre_text, "test_centre.txt")
    h5 = doc5.header
    
    assert h5.judicial_centre == "Edmonton", "Expected Edmonton, got " + h5.judicial_centre
    
    print("Test 5 passed: Judicial centre extraction from IN THE COURT line")
    
    print("")
    print("All header parsing tests passed!")

def test_sorting():
    """Test document sorting per CKB rules"""
    
    # Test sort key generation
    h1 = CKBHeader(
        court_file_number="2303-12345",
        judicial_centre="Calgary",
        plaintiff="John Smith",
        defendant="Jane Doe",
        document_type="Statement of Claim"
    )
    
    doc1 = CKBDocument(header=h1, filename="test1.txt")
    
    h2 = CKBHeader(
        court_file_number="2301-00567",
        judicial_centre="Edmonton",
        plaintiff="ABC Corp",
        defendant="XYZ Ltd",
        document_type="Affidavit"
    )
    
    doc2 = CKBDocument(header=h2, filename="test2.txt")
    
    # Calgary should sort before Edmonton
    assert doc1.sort_key()[0] < doc2.sort_key()[0], "Calgary should sort before Edmonton"
    
    # Both civil, plaintiff party type - check document type precedence
    # Statement of Claim (2) < Affidavit (6)
    assert doc1.sort_key()[4] < doc2.sort_key()[4], "Statement of Claim should sort before Affidavit"
    
    print("Sort key test passed: Calgary+StatementOfClaim sorts before Edmonton+Affidavit")

def test_precedence_values():
    """Test that precedence values are correctly ordered"""
    
    # Document type precedence: lower = higher priority
    assert DOCUMENT_TYPE_PRECEDENCE[DocumentType.ORIGINATING_APPLICATION] < DOCUMENT_TYPE_PRECEDENCE[DocumentType.STATEMENT_OF_CLAIM]
    assert DOCUMENT_TYPE_PRECEDENCE[DocumentType.STATEMENT_OF_CLAIM] < DOCUMENT_TYPE_PRECEDENCE[DocumentType.AFFIDAVIT]
    assert DOCUMENT_TYPE_PRECEDENCE[DocumentType.AFFIDAVIT] < DOCUMENT_TYPE_PRECEDENCE[DocumentType.APPLICATION]
    
    # Criminal types should come after civil originating docs
    assert DOCUMENT_TYPE_PRECEDENCE[DocumentType.INFORMATION] > DOCUMENT_TYPE_PRECEDENCE[DocumentType.ORIGINATING_APPLICATION]
    
    # Party type precedence
    assert PARTY_TYPE_PRECEDENCE[PartyType.PROSECUTION] < PARTY_TYPE_PRECEDENCE[PartyType.PLAINTIFF]
    assert PARTY_TYPE_PRECEDENCE[PartyType.PLAINTIFF] < PARTY_TYPE_PRECEDENCE[PartyType.DEFENDANT]
    assert PARTY_TYPE_PRECEDENCE[PartyType.DEFENDANT] < PARTY_TYPE_PRECEDENCE[PartyType.ACCUSED]
    
    # Jurisdiction precedence
    assert JURISDICTION_PRECEDENCE[Jurisdiction.CRIMINAL] < JURISDICTION_PRECEDENCE[Jurisdiction.CIVIL]
    assert JURISDICTION_PRECEDENCE[Jurisdiction.CIVIL] < JURISDICTION_PRECEDENCE[Jurisdiction.FAMILY]
    assert JURISDICTION_PRECEDENCE[Jurisdiction.FAMILY] < JURISDICTION_PRECEDENCE[Jurisdiction.SURROGATE]
    assert JURISDICTION_PRECEDENCE[Jurisdiction.SURROGATE] < JURISDICTION_PRECEDENCE[Jurisdiction.BANKRUPTCY]
    
    # Judicial centres alphabetical
    assert JUDICIAL_CENTRES == sorted(JUDICIAL_CENTRES)
    
    print("All precedence values correctly ordered!")

def test_integration():
    """Integration test with temporary files"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = Path(tmpdir) / "input"
        output_dir = Path(tmpdir) / "output"
        input_dir.mkdir()
        
        # Create test files
        test_files = {
            "calgary_2303-12345_claim.txt": """COURT FILE NUMBER: 2303-12345
JUDICIAL CENTRE: Calgary
PLAINTIFF: John Smith
DEFENDANT: Jane Doe
DOCUMENT: Statement of Claim
FILED ON: January 15, 2023""",
            
            "edmonton_2301-00567_affidavit.txt": """COURT FILE NUMBER: 2301-00567
JUDICIAL CENTRE: Edmonton
PLAINTIFF: ABC Corp
DEFENDANT: XYZ Ltd
DOCUMENT: Affidavit
FILED ON: February 20, 2023""",
            
            "lethbridge_2212-09876_info.txt": """COURT FILE NUMBER: 2212-09876
JUDICIAL CENTRE: Lethbridge
PROSECUTION: His Majesty the King
ACCUSED: Robert Johnson
DOCUMENT: Information
FILED ON: March 10, 2022""",
            
            "red_deer_2405-00123_parenting.txt": """COURT FILE NUMBER: 2405-00123
JUDICIAL CENTRE: Red Deer
PLAINTIFF: Sarah Wilson
DEFENDANT: Michael Wilson
DOCUMENT: Parenting Order
FILED ON: June 1, 2024""",
        }
        
        for filename, content in test_files.items():
            (input_dir / filename).write_text(content)
        
        # Run sorter
        sorter = CKBDocumentSorter(str(input_dir), str(output_dir))
        sorter.load_documents(['.txt'])
        
        assert len(sorter.documents) == 4, "Expected 4 documents, got " + str(len(sorter.documents))
        
        sorter.sort_documents()
        
        # Check sort order:
        # 1. Calgary (alphabetically first) - 2023 civil claim
        # 2. Edmonton - 2023 civil affidavit
        # 3. Lethbridge - 2022 criminal information
        # 4. Red Deer - 2024 family parenting order
        
        sorted_names = [d.filename for d in sorter.documents]
        print("Sort order: " + str(sorted_names))
        
        # Calgary should be first (alphabetically first judicial centre)
        assert sorted_names[0] == "calgary_2303-12345_claim.txt", "First should be Calgary, got " + sorted_names[0]
        
        # Export test
        md_output = sorter.export_sorted('md')
        assert "Alberta Court of King's Bench" in md_output
        assert "COURT FILE NUMBER" in md_output
        assert "JUDICIAL CENTRE" in md_output
        
        json_output = sorter.export_sorted('json')
        import json
        data = json.loads(json_output)
        assert data["total_documents"] == 4
        assert len(data["documents"]) == 4
        
        html_output = sorter.export_sorted('html')
        assert "<!DOCTYPE html>" in html_output
        assert "CKB Document Index" in html_output
        
        # Test copy
        sorter.copy_sorted_files()
        sorted_dir = output_dir / "sorted"
        copied_files = list(sorted_dir.glob("*"))
        assert len(copied_files) == 4
        
        print("Integration test passed!")

if __name__ == "__main__":
    print("Running CKB Document Sorter tests...")
    print("=" * 50)
    
    test_precedence_values()
    print("")
    
    test_header_parsing()
    print("")
    
    test_sorting()
    print("")
    
    test_integration()
    print("")
    
    print("=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)
