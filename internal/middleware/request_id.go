package middleware

import (
	"crypto/rand"
	"encoding/hex"
	"net/http"

	"github.com/gin-gonic/gin"
)

const (
	requestIDHeader = "X-Request-Id"
	requestIDKey    = "request_id"
)

func RequestID() gin.HandlerFunc {
	return func(c *gin.Context) {
		rid := c.GetHeader(requestIDHeader)
		if rid == "" {
			b := make([]byte, 16)
			if _, err := rand.Read(b); err == nil {
				rid = hex.EncodeToString(b)
			}
		}
		if rid != "" {
			c.Set(requestIDKey, rid)
			c.Writer.Header().Set(requestIDHeader, rid)
		}

		c.Next()
	}
}

func GetRequestID(c *gin.Context) string {
	if v, ok := c.Get(requestIDKey); ok {
		if s, ok := v.(string); ok {
			return s
		}
	}
	return ""
}

func RequestIDHeaderName() string {
	return requestIDHeader
}

func RequestIDFromResponse(w http.ResponseWriter) string {
	return w.Header().Get(requestIDHeader)
}
