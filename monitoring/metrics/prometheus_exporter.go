package metrics

import (
	"log"
	"math/rand"
	"net/http"
	"runtime"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// Custom metric structs
var (
	httpRequestsTotal = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Total number of HTTP requests received.",
		},
		[]string{"method", "endpoint"},
	)

	httpRequestDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_request_duration_seconds",
			Help:    "Duration of HTTP requests in seconds.",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "endpoint"},
	)

	transactionProcessedTotal = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "transaction_processed_total",
			Help: "Total number of transactions processed.",
		},
		[]string{"status", "type"},
	)

	transactionProcessingDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "transaction_processing_duration_seconds",
			Help:    "Duration of transaction processing in seconds.",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"status", "type"},
	)

	memoryUsage = prometheus.NewGaugeFunc(
		prometheus.GaugeOpts{
			Name: "memory_usage_bytes",
			Help: "Current memory usage in bytes.",
		},
		func() float64 {
			var m runtime.MemStats
			runtime.ReadMemStats(&m)
			return float64(m.Alloc)
		},
	)

	goroutines = prometheus.NewGaugeFunc(
		prometheus.GaugeOpts{
			Name: "goroutines",
			Help: "Current number of goroutines.",
		},
		func() float64 {
			return float64(runtime.NumGoroutine())
		},
	)
)

// Register all metrics
func init() {
	prometheus.MustRegister(httpRequestsTotal)
	prometheus.MustRegister(httpRequestDuration)
	prometheus.MustRegister(transactionProcessedTotal)
	prometheus.MustRegister(transactionProcessingDuration)
	prometheus.MustRegister(memoryUsage)
	prometheus.MustRegister(goroutines)
}

// Middleware to track HTTP request metrics
func MetricsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		method := r.Method
		endpoint := r.URL.Path

		timer := prometheus.NewTimer(httpRequestDuration.WithLabelValues(method, endpoint))
		defer timer.ObserveDuration()

		httpRequestsTotal.WithLabelValues(method, endpoint).Inc()
		next.ServeHTTP(w, r)
	})
}

// Track transaction processing time and status
func TrackTransactionProcessing(status, transactionType string, processingTime time.Duration) {
	transactionProcessedTotal.WithLabelValues(status, transactionType).Inc()
	transactionProcessingDuration.WithLabelValues(status, transactionType).Observe(processingTime.Seconds())
}

// Start the Prometheus exporter on a given port
func StartPrometheusExporter(port string) {
	http.Handle("/metrics", promhttp.Handler())
	err := http.ListenAndServe(":"+port, nil)
	if err != nil {
		log.Fatal("Failed to start Prometheus exporter: ", err)
	}
}

// Periodically log memory usage and goroutines
func StartSystemMetricsLogging(interval time.Duration) {
	ticker := time.NewTicker(interval)
	go func() {
		for range ticker.C {
			var m runtime.MemStats
			runtime.ReadMemStats(&m)
			memoryUsage.Set(float64(m.Alloc))
			goroutines.Set(float64(runtime.NumGoroutine()))
		}
	}()
}

// Function to process the transaction with a random success or failure result
func ProcessTransaction(transactionType string) string {
	start := time.Now()

	// Simulate transaction processing logic
	processingTime := rand.Intn(3000) + 500 // Random delay between 500ms to 3.5s
	time.Sleep(time.Duration(processingTime) * time.Millisecond)

	duration := time.Since(start)
	if rand.Float32() < 0.85 { // 85% success rate
		TrackTransactionProcessing("success", transactionType, duration)
		return "success"
	} else {
		TrackTransactionProcessing("failure", transactionType, duration)
		return "failure"
	}
}

// HTTP handler for triggering a transaction
func TransactionHandler(w http.ResponseWriter, r *http.Request) {
	transactionType := r.URL.Query().Get("type")
	if transactionType == "" {
		transactionType = "payment"
	}

	status := ProcessTransaction(transactionType)
	if status == "success" {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("Transaction processed successfully"))
	} else {
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte("Transaction failed"))
	}
}

// HTTP handler for health check
func HealthCheckHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("OK"))
}

func main() {
	// Start Prometheus exporter
	go StartPrometheusExporter("2112")

	// Log system metrics every 10 seconds
	StartSystemMetricsLogging(10 * time.Second)

	// Set up HTTP routes
	mux := http.NewServeMux()
	mux.HandleFunc("/health", HealthCheckHandler)
	mux.Handle("/transaction", MetricsMiddleware(http.HandlerFunc(TransactionHandler)))

	// Start the HTTP server
	err := http.ListenAndServe(":8080", mux)
	if err != nil {
		log.Fatal("Failed to start server: ", err)
	}
}
