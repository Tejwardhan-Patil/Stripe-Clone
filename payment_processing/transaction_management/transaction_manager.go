package transaction_management

import (
	"database/sql"
	"errors"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/google/uuid"
	_ "github.com/lib/pq"
)

// Transaction represents a payment transaction
type Transaction struct {
	ID             string
	UserID         string
	Amount         float64
	Currency       string
	Status         string
	CreatedAt      time.Time
	LastModifiedAt time.Time
}

// TransactionManager handles transaction-related operations
type TransactionManager struct {
	db   *sql.DB
	lock sync.Mutex
}

// NewTransactionManager initializes a new TransactionManager
func NewTransactionManager(dataSourceName string) (*TransactionManager, error) {
	db, err := sql.Open("postgres", dataSourceName)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %v", err)
	}
	return &TransactionManager{db: db}, nil
}

// CreateTransaction initializes a new transaction
func (tm *TransactionManager) CreateTransaction(userID string, amount float64, currency string) (*Transaction, error) {
	tm.lock.Lock()
	defer tm.lock.Unlock()

	tx, err := tm.db.Begin()
	if err != nil {
		return nil, fmt.Errorf("failed to begin transaction: %v", err)
	}

	transaction := &Transaction{
		ID:             generateUUID(),
		UserID:         userID,
		Amount:         amount,
		Currency:       currency,
		Status:         "PENDING",
		CreatedAt:      time.Now(),
		LastModifiedAt: time.Now(),
	}

	query := `INSERT INTO transactions (id, user_id, amount, currency, status, created_at, last_modified_at) VALUES ($1, $2, $3, $4, $5, $6, $7)`
	_, err = tx.Exec(query, transaction.ID, transaction.UserID, transaction.Amount, transaction.Currency, transaction.Status, transaction.CreatedAt, transaction.LastModifiedAt)
	if err != nil {
		tx.Rollback()
		return nil, fmt.Errorf("failed to insert transaction: %v", err)
	}

	if err := tx.Commit(); err != nil {
		return nil, fmt.Errorf("failed to commit transaction: %v", err)
	}

	return transaction, nil
}

// UpdateTransactionStatus updates the status of a transaction
func (tm *TransactionManager) UpdateTransactionStatus(transactionID, status string) error {
	tm.lock.Lock()
	defer tm.lock.Unlock()

	tx, err := tm.db.Begin()
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %v", err)
	}

	query := `UPDATE transactions SET status = $1, last_modified_at = $2 WHERE id = $3`
	_, err = tx.Exec(query, status, time.Now(), transactionID)
	if err != nil {
		tx.Rollback()
		return fmt.Errorf("failed to update transaction status: %v", err)
	}

	if err := tx.Commit(); err != nil {
		return fmt.Errorf("failed to commit transaction: %v", err)
	}

	return nil
}

// GetTransaction retrieves a transaction by its ID
func (tm *TransactionManager) GetTransaction(transactionID string) (*Transaction, error) {
	query := `SELECT id, user_id, amount, currency, status, created_at, last_modified_at FROM transactions WHERE id = $1`
	row := tm.db.QueryRow(query, transactionID)

	transaction := &Transaction{}
	err := row.Scan(&transaction.ID, &transaction.UserID, &transaction.Amount, &transaction.Currency, &transaction.Status, &transaction.CreatedAt, &transaction.LastModifiedAt)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, fmt.Errorf("transaction not found: %v", err)
		}
		return nil, fmt.Errorf("failed to get transaction: %v", err)
	}

	return transaction, nil
}

// DeleteTransaction deletes a transaction by its ID
func (tm *TransactionManager) DeleteTransaction(transactionID string) error {
	tm.lock.Lock()
	defer tm.lock.Unlock()

	tx, err := tm.db.Begin()
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %v", err)
	}

	query := `DELETE FROM transactions WHERE id = $1`
	_, err = tx.Exec(query, transactionID)
	if err != nil {
		tx.Rollback()
		return fmt.Errorf("failed to delete transaction: %v", err)
	}

	if err := tx.Commit(); err != nil {
		return fmt.Errorf("failed to commit transaction: %v", err)
	}

	return nil
}

// generateUUID generates a unique identifier for transactions.
func generateUUID() string {
	return uuid.New().String()
}

// Close closes the database connection
func (tm *TransactionManager) Close() error {
	return tm.db.Close()
}

func main() {
	dataSourceName := "user=username dbname=transactions sslmode=disable"
	manager, err := NewTransactionManager(dataSourceName)
	if err != nil {
		log.Fatalf("failed to create transaction manager: %v", err)
	}
	defer manager.Close()

	// Usage
	transaction, err := manager.CreateTransaction("user123", 100.0, "USD")
	if err != nil {
		log.Printf("error creating transaction: %v", err)
	} else {
		log.Printf("transaction created: %+v", transaction)
	}
}
