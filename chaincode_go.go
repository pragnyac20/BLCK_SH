package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// SmartContract provides functions for managing academic records
type SmartContract struct {
	contractapi.Contract
}

// Anchor represents an academic record anchor on the blockchain
type Anchor struct {
	RecordID  string `json:"recordID"`
	Anchor    string `json:"anchor"`
	Issuer    string `json:"issuer"`
	Time      string `json:"time"`
	Version   int    `json:"version"`
	UpdateLog []UpdateEntry `json:"updateLog"`
}

// UpdateEntry represents a record update
type UpdateEntry struct {
	NewAnchor string `json:"newAnchor"`
	Reason    string `json:"reason"`
	Timestamp string `json:"timestamp"`
	UpdatedBy string `json:"updatedBy"`
}

// IssueRecord creates a new academic record anchor on the ledger
func (s *SmartContract) IssueRecord(ctx contractapi.TransactionContextInterface, recordID string, anchor string, issuer string) error {
	// Check if record already exists
	exists, err := s.AnchorExists(ctx, recordID)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("record %s already exists", recordID)
	}

	// Get client identity (in production, verify authorized issuer)
	// clientID, err := ctx.GetClientIdentity().GetID()
	// if err != nil {
	// 	return fmt.Errorf("failed to get client identity: %v", err)
	// }

	// Create anchor
	anchorRecord := Anchor{
		RecordID:  recordID,
		Anchor:    anchor,
		Issuer:    issuer,
		Time:      time.Now().Format(time.RFC3339),
		Version:   1,
		UpdateLog: []UpdateEntry{},
	}

	// Marshal to JSON
	anchorJSON, err := json.Marshal(anchorRecord)
	if err != nil {
		return err
	}

	// Save to ledger
	return ctx.GetStub().PutState(recordID, anchorJSON)
}

// UpdateRecord updates an existing record with a new anchor
func (s *SmartContract) UpdateRecord(ctx contractapi.TransactionContextInterface, recordID string, newAnchor string, reason string, updatedBy string) error {
	// Get existing record
	anchor, err := s.GetAnchor(ctx, recordID)
	if err != nil {
		return err
	}

	// Create update entry
	updateEntry := UpdateEntry{
		NewAnchor: newAnchor,
		Reason:    reason,
		Timestamp: time.Now().Format(time.RFC3339),
		UpdatedBy: updatedBy,
	}

	// Update the anchor
	anchor.UpdateLog = append(anchor.UpdateLog, updateEntry)
	anchor.Anchor = newAnchor
	anchor.Version++

	// Marshal and save
	anchorJSON, err := json.Marshal(anchor)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(recordID, anchorJSON)
}

// GetAnchor retrieves an anchor from the ledger
func (s *SmartContract) GetAnchor(ctx contractapi.TransactionContextInterface, recordID string) (*Anchor, error) {
	anchorJSON, err := ctx.GetStub().GetState(recordID)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if anchorJSON == nil {
		return nil, fmt.Errorf("record %s does not exist", recordID)
	}

	var anchor Anchor
	err = json.Unmarshal(anchorJSON, &anchor)
	if err != nil {
		return nil, err
	}

	return &anchor, nil
}

// AnchorExists checks if an anchor exists in the ledger
func (s *SmartContract) AnchorExists(ctx contractapi.TransactionContextInterface, recordID string) (bool, error) {
	anchorJSON, err := ctx.GetStub().GetState(recordID)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}

	return anchorJSON != nil, nil
}

// VerifyRecord verifies if a supplied anchor matches the on-chain anchor
func (s *SmartContract) VerifyRecord(ctx contractapi.TransactionContextInterface, recordID string, suppliedAnchor string) (bool, error) {
	anchor, err := s.GetAnchor(ctx, recordID)
	if err != nil {
		return false, err
	}

	return anchor.Anchor == suppliedAnchor, nil
}

// GetRecordHistory retrieves the history of a record
func (s *SmartContract) GetRecordHistory(ctx contractapi.TransactionContextInterface, recordID string) ([]Anchor, error) {
	resultsIterator, err := ctx.GetStub().GetHistoryForKey(recordID)
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var history []Anchor
	for resultsIterator.HasNext() {
		response, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var anchor Anchor
		if err := json.Unmarshal(response.Value, &anchor); err != nil {
			return nil, err
		}
		history = append(history, anchor)
	}

	return history, nil
}

// GetAllRecords retrieves all records (use with caution in production)
func (s *SmartContract) GetAllRecords(ctx contractapi.TransactionContextInterface) ([]*Anchor, error) {
	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var anchors []*Anchor
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var anchor Anchor
		err = json.Unmarshal(queryResponse.Value, &anchor)
		if err != nil {
			return nil, err
		}
		anchors = append(anchors, &anchor)
	}

	return anchors, nil
}

// DeleteRecord deletes a record (use with extreme caution)
func (s *SmartContract) DeleteRecord(ctx contractapi.TransactionContextInterface, recordID string) error {
	exists, err := s.AnchorExists(ctx, recordID)
	if err != nil {
		return err
	}
	if !exists {
		return fmt.Errorf("record %s does not exist", recordID)
	}

	return ctx.GetStub().DelState(recordID)
}

func main() {
	chaincode, err := contractapi.NewChaincode(&SmartContract{})
	if err != nil {
		fmt.Printf("Error creating education chaincode: %v\n", err)
		return
	}

	if err := chaincode.Start(); err != nil {
		fmt.Printf("Error starting education chaincode: %v\n", err)
	}
}