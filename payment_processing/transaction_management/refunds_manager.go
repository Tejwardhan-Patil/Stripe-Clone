package transaction_management

import (
	"database/sql"
	"errors"
	"fmt"
	"sync"
	"time"

	_ "github.com/lib/pq"
)

// Refund represents a refund for a transaction
type Refund struct {
	ID             string
	TransactionID  string
	UserID         string
	Amount         float64
	Status         string
	CreatedAt      time.Time
	LastModifiedAt time.Time
}

// RefundsManager handles refund-related operations
type RefundsManager struct {
	db   *sql.DB
	lock sync.Mutex
}

// NewRefundsManager initializes a new RefundsManager
func NewRefundsManager(dataSourceName string) (*RefundsManager, error) {
	db, err := sql.Open("postgres", dataSourceName)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %v", err)
	}
	return &RefundsManager{db: db}, nil
}

// CreateRefund initiates a new refund for a given transaction
func (rm *RefundsManager) CreateRefund(transactionID string, userID string, amount float64) (*Refund, error) {
	rm.lock.Lock()
	defer rm.lock.Unlock()

	tx, err := rm.db.Begin()
	if err != nil {
		return nil, fmt.Errorf("failed to begin transaction: %v", err)
	}

	refund := &Refund{
		ID:             generateUUID(),
		TransactionID:  transactionID,
		UserID:         userID,
		Amount:         amount,
		Status:         "PENDING",
		CreatedAt:      time.Now(),
		LastModifiedAt: time.Now(),
	}

	query := `INSERT INTO refunds (id, transaction_id, user_id, amount, status, created_at, last_modified_at) VALUES ($1, $2, $3, $4, $5, $6, $7)`
	_, err = tx.Exec(query, refund.ID, refund.TransactionID, refund.UserID, refund.Amount, refund.Status, refund.CreatedAt, refund.LastModifiedAt)
	if err != nil {
		tx.Rollback()
		return nil, fmt.Errorf("failed to insert refund: %v", err)
	}

	if err := tx.Commit(); err != nil {
		return nil, fmt.Errorf("failed to commit refund: %v", err)
	}

	return refund, nil
}

// UpdateRefundStatus updates the status of a refund
func (rm *RefundsManager) UpdateRefundStatus(refundID, status string) error {
	rm.lock.Lock()
	defer rm.lock.Unlock()

	tx, err := rm.db.Begin()
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %v", err)
	}

	query := `UPDATE refunds SET status = $1, last_modified_at = $2 WHERE id = $3`
	_, err = tx.Exec(query, status, time.Now(), refundID)
	if err != nil {
		tx.Rollback()
		return fmt.Errorf("failed to update refund status: %v", err)
	}

	if err := tx.Commit(); err != nil {
		return fmt.Errorf("failed to commit refund update: %v", err)
	}

	return nil
}

// GetRefund retrieves a refund by its ID
func (rm *RefundsManager) GetRefund(refundID string) (*Refund, error) {
	query := `SELECT id, transaction_id, user_id, amount, status, created_at, last_modified_at FROM refunds WHERE id = $1`
	row := rm.db.QueryRow(query, refundID)

	refund := &Refund{}
	err := row.Scan(&refund.ID, &refund.TransactionID, &refund.UserID, &refund.Amount, &refund.Status, &refund.CreatedAt, &refund.LastModifiedAt)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, fmt.Errorf("refund not found: %v", err)
		}
		return nil, fmt.Errorf("failed to get refund: %v", err)
	}

	return refund, nil
}

// ListRefundsByTransaction retrieves all refunds related to a specific transaction
func (rm *RefundsManager) ListRefundsByTransaction(transactionID string) ([]*Refund, error) {
	query := `SELECT id, transaction_id, user_id, amount, status, created_at, last_modified_at FROM refunds WHERE transaction_id = $1`
	rows, err := rm.db.Query(query, transactionID)
	if err != nil {
		return nil, fmt.Errorf("failed to list refunds: %v", err)
	}
	defer rows.Close()

	var refunds []*Refund
	for rows.Next() {
		refund := &Refund{}
		err := rows.Scan(&refund.ID, &refund.TransactionID, &refund.UserID, &refund.Amount, &refund.Status, &refund.CreatedAt, &refund.LastModifiedAt)
		if err != nil {
			return nil, fmt.Errorf("failed to scan refund: %v", err)
		}
		refunds = append(refunds, refund)
	}

	return refunds, nil
}

// DeleteRefund deletes a refund by its ID
func (rm *RefundsManager) DeleteRefund(refundID string) error {
	rm.lock.Lock()
	defer rm.lock.Unlock()

	tx, err := rm.db.Begin()
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %v", err)
	}

	query := `DELETE FROM refunds WHERE id = $1`
	_, err = tx.Exec(query, refundID)
	if err != nil {
		tx.Rollback()
		return fmt.Errorf("failed to delete refund: %v", err)
	}

	if err := tx.Commit(); err != nil {
		return fmt.Errorf("failed to commit refund deletion: %v", err)
	}

	return nil
}
