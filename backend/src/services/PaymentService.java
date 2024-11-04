package backend.src.services;

import java.math.BigDecimal;
import java.util.Currency;
import java.util.UUID;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import com.fasterxml.jackson.databind.ObjectMapper; 

public class PaymentService {

    private final String PAYMENT_API_URL = "http://localhost:5000/api/payment";  
    private final String JWT_API_URL = "http://localhost:5000/api/jwt";
    private final String EMAIL_API_URL = "http://localhost:5000/api/email";

    private ObjectMapper objectMapper;

    public PaymentService() {
        this.objectMapper = new ObjectMapper();
    }

    public PaymentResponse processPayment(PaymentRequest paymentRequest) {
        validatePaymentRequest(paymentRequest);

        Optional<String> userId = getUserIdFromToken(paymentRequest.getJwtToken());
        if (!userId.isPresent()) {
            throw new IllegalStateException("Invalid JWT token");
        }

        Map<String, Object> paymentData = new HashMap<>();
        paymentData.put("id", UUID.randomUUID().toString());
        paymentData.put("user_id", userId.get());
        paymentData.put("amount", paymentRequest.getAmount());
        paymentData.put("currency", paymentRequest.getCurrency());
        paymentData.put("payment_method", paymentRequest.getPaymentMethod());
        paymentData.put("status", "PENDING");

        try {
            String paymentResponse = sendPostRequest(PAYMENT_API_URL, paymentData);
            Map<String, Object> responseMap = objectMapper.readValue(paymentResponse, Map.class);

            sendEmailNotification(responseMap);

            return new PaymentResponse(
                    (String) responseMap.get("id"),
                    (String) responseMap.get("status"),
                    new BigDecimal((String) responseMap.get("amount")),
                    (String) responseMap.get("currency")
            );
        } catch (Exception e) {
            throw new RuntimeException("Payment processing failed: " + e.getMessage());
        }
    }

    public RefundResponse processRefund(String paymentId, BigDecimal refundAmount) {
        try {
            Map<String, Object> refundData = new HashMap<>();
            refundData.put("payment_id", paymentId);
            refundData.put("refund_amount", refundAmount);

            String refundResponse = sendPostRequest(PAYMENT_API_URL + "/refund", refundData);
            Map<String, Object> responseMap = objectMapper.readValue(refundResponse, Map.class);

            return new RefundResponse(paymentId, (String) responseMap.get("status"), refundAmount);
        } catch (Exception e) {
            throw new RuntimeException("Refund processing failed: " + e.getMessage());
        }
    }

    private void validatePaymentRequest(PaymentRequest request) {
        if (request.getAmount() == null || request.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Invalid payment amount");
        }
        if (request.getCurrency() == null || !Currency.getAvailableCurrencies().contains(Currency.getInstance(request.getCurrency()))) {
            throw new IllegalArgumentException("Invalid currency");
        }
        if (request.getPaymentMethod() == null || request.getPaymentMethod().isEmpty()) {
            throw new IllegalArgumentException("Payment method is required");
        }
    }

    private Optional<String> getUserIdFromToken(String jwtToken) {
        try {
            Map<String, Object> tokenData = new HashMap<>();
            tokenData.put("token", jwtToken);

            String jwtResponse = sendPostRequest(JWT_API_URL + "/validate", tokenData);
            Map<String, Object> responseMap = objectMapper.readValue(jwtResponse, Map.class);

            return Optional.ofNullable((String) responseMap.get("user_id"));
        } catch (Exception e) {
            return Optional.empty();
        }
    }

    private void sendEmailNotification(Map<String, Object> paymentData) throws Exception {
        Map<String, Object> emailData = new HashMap<>();
        emailData.put("user_id", paymentData.get("user_id"));
        emailData.put("payment_id", paymentData.get("id"));
        emailData.put("status", paymentData.get("status"));

        sendPostRequest(EMAIL_API_URL + "/send_confirmation", emailData);
    }

    private String sendPostRequest(String urlString, Map<String, Object> payload) throws Exception {
        URL url = new URL(urlString);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json; utf-8");
        conn.setRequestProperty("Accept", "application/json");
        conn.setDoOutput(true);

        String jsonInputString = objectMapper.writeValueAsString(payload);

        try (OutputStream os = conn.getOutputStream()) {
            byte[] input = jsonInputString.getBytes(StandardCharsets.UTF_8);
            os.write(input, 0, input.length);
        }

        try (BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream(), StandardCharsets.UTF_8))) {
            StringBuilder response = new StringBuilder();
            String responseLine;
            while ((responseLine = br.readLine()) != null) {
                response.append(responseLine.trim());
            }
            return response.toString();
        }
    }

    public static class PaymentRequest {
        private BigDecimal amount;
        private String currency;
        private String paymentMethod;
        private String jwtToken;

        public BigDecimal getAmount() {
            return amount;
        }

        public void setAmount(BigDecimal amount) {
            this.amount = amount;
        }

        public String getCurrency() {
            return currency;
        }

        public void setCurrency(String currency) {
            this.currency = currency;
        }

        public String getPaymentMethod() {
            return paymentMethod;
        }

        public void setPaymentMethod(String paymentMethod) {
            this.paymentMethod = paymentMethod;
        }

        public String getJwtToken() {
            return jwtToken;
        }

        public void setJwtToken(String jwtToken) {
            this.jwtToken = jwtToken;
        }
    }

    public static class PaymentResponse {
        private String paymentId;
        private String status;
        private BigDecimal amount;
        private String currency;

        public PaymentResponse(String paymentId, String status, BigDecimal amount, String currency) {
            this.paymentId = paymentId;
            this.status = status;
            this.amount = amount;
            this.currency = currency;
        }

        public String getPaymentId() {
            return paymentId;
        }

        public void setPaymentId(String paymentId) {
            this.paymentId = paymentId;
        }

        public String getStatus() {
            return status;
        }

        public void setStatus(String status) {
            this.status = status;
        }

        public BigDecimal getAmount() {
            return amount;
        }

        public void setAmount(BigDecimal amount) {
            this.amount = amount;
        }

        public String getCurrency() {
            return currency;
        }

        public void setCurrency(String currency) {
            this.currency = currency;
        }
    }

    public static class RefundResponse {
        private String paymentId;
        private String status;
        private BigDecimal refundAmount;

        public RefundResponse(String paymentId, String status, BigDecimal refundAmount) {
            this.paymentId = paymentId;
            this.status = status;
            this.refundAmount = refundAmount;
        }

        public String getPaymentId() {
            return paymentId;
        }

        public void setPaymentId(String paymentId) {
            this.paymentId = paymentId;
        }

        public String getStatus() {
            return status;
        }

        public void setStatus(String status) {
            this.status = status;
        }

        public BigDecimal getRefundAmount() {
            return refundAmount;
        }

        public void setRefundAmount(BigDecimal refundAmount) {
            this.refundAmount = refundAmount;
        }
    }
}