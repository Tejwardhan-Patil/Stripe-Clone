package caching

import (
	"context"
	"errors"
	"github.com/go-redis/redis/v8"
	"log"
	"time"
)

// RedisCache is the struct to handle the Redis client and context
type RedisCache struct {
	client *redis.Client
	ctx    context.Context
}

// NewRedisCache initializes a new RedisCache
func NewRedisCache(redisAddr, redisPassword string, db int) *RedisCache {
	rdb := redis.NewClient(&redis.Options{
		Addr:     redisAddr,
		Password: redisPassword,
		DB:       db,
	})

	ctx := context.Background()

	return &RedisCache{
		client: rdb,
		ctx:    ctx,
	}
}

// Set stores a key-value pair in Redis with an expiration time
func (cache *RedisCache) Set(key string, value interface{}, expiration time.Duration) error {
	err := cache.client.Set(cache.ctx, key, value, expiration).Err()
	if err != nil {
		log.Printf("Error setting value in cache: %v", err)
		return err
	}
	return nil
}

// Get retrieves a value from Redis based on the key
func (cache *RedisCache) Get(key string) (string, error) {
	val, err := cache.client.Get(cache.ctx, key).Result()
	if err == redis.Nil {
		return "", errors.New("key does not exist")
	} else if err != nil {
		log.Printf("Error getting value from cache: %v", err)
		return "", err
	}
	return val, nil
}

// Delete removes a key from Redis
func (cache *RedisCache) Delete(key string) error {
	err := cache.client.Del(cache.ctx, key).Err()
	if err != nil {
		log.Printf("Error deleting key from cache: %v", err)
		return err
	}
	return nil
}

// FlushAll clears all keys from Redis
func (cache *RedisCache) FlushAll() error {
	err := cache.client.FlushAll(cache.ctx).Err()
	if err != nil {
		log.Printf("Error flushing cache: %v", err)
		return err
	}
	return nil
}

// TTL retrieves the time-to-live of a key in Redis
func (cache *RedisCache) TTL(key string) (time.Duration, error) {
	ttl, err := cache.client.TTL(cache.ctx, key).Result()
	if err != nil {
		log.Printf("Error fetching TTL: %v", err)
		return 0, err
	}
	return ttl, nil
}

// Incr increments the integer value of a key by one
func (cache *RedisCache) Incr(key string) (int64, error) {
	result, err := cache.client.Incr(cache.ctx, key).Result()
	if err != nil {
		log.Printf("Error incrementing value: %v", err)
		return 0, err
	}
	return result, nil
}

// Decr decrements the integer value of a key by one
func (cache *RedisCache) Decr(key string) (int64, error) {
	result, err := cache.client.Decr(cache.ctx, key).Result()
	if err != nil {
		log.Printf("Error decrementing value: %v", err)
		return 0, err
	}
	return result, nil
}

// SetNX sets a key only if it does not already exist
func (cache *RedisCache) SetNX(key string, value interface{}, expiration time.Duration) (bool, error) {
	result, err := cache.client.SetNX(cache.ctx, key, value, expiration).Result()
	if err != nil {
		log.Printf("Error setting value with SetNX: %v", err)
		return false, err
	}
	return result, nil
}

// Exists checks if a key exists in Redis
func (cache *RedisCache) Exists(key string) (bool, error) {
	result, err := cache.client.Exists(cache.ctx, key).Result()
	if err != nil {
		log.Printf("Error checking if key exists: %v", err)
		return false, err
	}
	return result > 0, nil
}

// HSet sets a hash field in Redis
func (cache *RedisCache) HSet(key string, field string, value interface{}) error {
	err := cache.client.HSet(cache.ctx, key, field, value).Err()
	if err != nil {
		log.Printf("Error setting hash value: %v", err)
		return err
	}
	return nil
}

// HGet retrieves a hash field from Redis
func (cache *RedisCache) HGet(key, field string) (string, error) {
	val, err := cache.client.HGet(cache.ctx, key, field).Result()
	if err == redis.Nil {
		return "", errors.New("hash field does not exist")
	} else if err != nil {
		log.Printf("Error getting hash value: %v", err)
		return "", err
	}
	return val, nil
}

// HDel deletes a hash field from Redis
func (cache *RedisCache) HDel(key string, fields ...string) error {
	err := cache.client.HDel(cache.ctx, key, fields...).Err()
	if err != nil {
		log.Printf("Error deleting hash field: %v", err)
		return err
	}
	return nil
}

// LPush adds an element to the head of a list in Redis
func (cache *RedisCache) LPush(key string, values ...interface{}) error {
	err := cache.client.LPush(cache.ctx, key, values...).Err()
	if err != nil {
		log.Printf("Error pushing value to list: %v", err)
		return err
	}
	return nil
}

// RPop removes an element from the tail of a list in Redis
func (cache *RedisCache) RPop(key string) (string, error) {
	val, err := cache.client.RPop(cache.ctx, key).Result()
	if err == redis.Nil {
		return "", errors.New("list is empty")
	} else if err != nil {
		log.Printf("Error popping value from list: %v", err)
		return "", err
	}
	return val, nil
}

// SAdd adds a member to a set in Redis
func (cache *RedisCache) SAdd(key string, members ...interface{}) error {
	err := cache.client.SAdd(cache.ctx, key, members...).Err()
	if err != nil {
		log.Printf("Error adding members to set: %v", err)
		return err
	}
	return nil
}

// SRem removes a member from a set in Redis
func (cache *RedisCache) SRem(key string, members ...interface{}) error {
	err := cache.client.SRem(cache.ctx, key, members...).Err()
	if err != nil {
		log.Printf("Error removing members from set: %v", err)
		return err
	}
	return nil
}

// SMembers returns all members of a set in Redis
func (cache *RedisCache) SMembers(key string) ([]string, error) {
	val, err := cache.client.SMembers(cache.ctx, key).Result()
	if err != nil {
		log.Printf("Error getting set members: %v", err)
		return nil, err
	}
	return val, nil
}

// Expire sets an expiration time on a key in Redis
func (cache *RedisCache) Expire(key string, expiration time.Duration) error {
	err := cache.client.Expire(cache.ctx, key, expiration).Err()
	if err != nil {
		log.Printf("Error setting expiration: %v", err)
		return err
	}
	return nil
}
