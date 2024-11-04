package backend.src.services;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import com.fasterxml.jackson.databind.ObjectMapper;

public class SubscriptionService {

    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;

    public SubscriptionService() {
        this.httpClient = HttpClient.newHttpClient();
        this.objectMapper = new ObjectMapper();
    }

    /**
     * Create a new subscription for a user
     * 
     * @param userToken JWT token representing the user
     * @param planId    Plan ID for the subscription
     * @return Created subscription details
     */
    public Optional<Map<String, Object>> createSubscription(String userToken, String planId) {
        // Validate user token via Python backend
        Optional<Map<String, Object>> userOpt = validateUserToken(userToken);

        if (userOpt.isPresent()) {
            Map<String, Object> user = userOpt.get();

            // Creating a subscription as a map
            Map<String, Object> subscription = new HashMap<>();
            subscription.put("userId", user.get("id"));
            subscription.put("planId", planId);
            subscription.put("startDate", LocalDate.now());
            subscription.put("endDate", calculateEndDate(planId));
            subscription.put("status", "active");

            // Save subscription via Python backend
            if (saveSubscription(subscription)) {
                // Send confirmation email via Python backend
                sendSubscriptionConfirmation(user.get("email").toString(), subscription);
                return Optional.of(subscription);
            }
        }
        return Optional.empty();
    }

    /**
     * Validate the JWT token by sending a request to the Python backend
     * 
     * @param token JWT token to validate
     * @return Optional containing user data if valid, empty otherwise
     */
    private Optional<Map<String, Object>> validateUserToken(String token) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(new URI("http://localhost:5000/auth/validate-token"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString("{\"token\": \"" + token + "\"}"))
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() == 200) {
                Map<String, Object> userData = objectMapper.readValue(response.body(), Map.class);
                return Optional.of(userData);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return Optional.empty();
    }

    /**
     * Save subscription by sending a request to the Python backend
     * 
     * @param subscription Subscription details to save
     * @return boolean indicating success or failure
     */
    private boolean saveSubscription(Map<String, Object> subscription) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(new URI("http://localhost:5000/subscriptions/create"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(objectMapper.writeValueAsString(subscription)))
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            return response.statusCode() == 200;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    /**
     * Send subscription confirmation email by sending a request to the Python backend
     * 
     * @param email         User email
     * @param subscription  Subscription details
     */
    private void sendSubscriptionConfirmation(String email, Map<String, Object> subscription) {
        try {
            Map<String, Object> payload = new HashMap<>();
            payload.put("email", email);
            payload.put("subscription", subscription);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(new URI("http://localhost:5000/email/send-subscription-confirmation"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(objectMapper.writeValueAsString(payload)))
                    .build();

            httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * Calculate end date for a subscription based on the plan
     * 
     * @param planId Plan ID to calculate the end date
     * @return End date as LocalDate
     */
    private LocalDate calculateEndDate(String planId) {
        if (planId.equals("monthly")) {
            return LocalDate.now().plusMonths(1);
        } else if (planId.equals("yearly")) {
            return LocalDate.now().plusYears(1);
        }
        return LocalDate.now();
    }

    /**
     * Cancel an existing subscription
     * 
     * @param userToken   JWT token representing the user
     * @param subscriptionId ID of the subscription to be canceled
     * @return boolean indicating success or failure of cancellation
     */
    public boolean cancelSubscription(String userToken, String subscriptionId) {
        // Validate user token via Python backend
        Optional<Map<String, Object>> userOpt = validateUserToken(userToken);
        
        if (userOpt.isPresent()) {
            try {
                Map<String, Object> payload = new HashMap<>();
                payload.put("subscriptionId", subscriptionId);
                payload.put("userId", userOpt.get().get("id"));

                HttpRequest request = HttpRequest.newBuilder()
                        .uri(new URI("http://localhost:5000/subscriptions/cancel"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(objectMapper.writeValueAsString(payload)))
                        .build();

                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                return response.statusCode() == 200;
            } catch (Exception e) {
                e.printStackTrace();
                return false;
            }
        }
        return false;
    }

    /**
     * Retrieve all active subscriptions for a user
     * 
     * @param userToken JWT token representing the user
     * @return List of active subscriptions
     */
    public List<Map<String, Object>> getActiveSubscriptions(String userToken) {
        // Validate user token via Python backend
        Optional<Map<String, Object>> userOpt = validateUserToken(userToken);

        if (userOpt.isPresent()) {
            try {
                HttpRequest request = HttpRequest.newBuilder()
                        .uri(new URI("http://localhost:5000/subscriptions/active"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString("{\"userId\": \"" + userOpt.get().get("id") + "\"}"))
                        .build();

                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                if (response.statusCode() == 200) {
                    return objectMapper.readValue(response.body(), List.class);
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        return List.of();
    }

}