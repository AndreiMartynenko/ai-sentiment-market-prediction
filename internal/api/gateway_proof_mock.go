package api

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"net/http"

	"github.com/gin-gonic/gin"
)

type mockProofRequest struct {
	Signal any `json:"signal" binding:"required"`
}

func PublishMockProof() gin.HandlerFunc {
	return func(c *gin.Context) {
		var reqBody mockProofRequest
		if err := c.ShouldBindJSON(&reqBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		b, err := json.Marshal(reqBody.Signal)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to encode signal"})
			return
		}

		h := sha256.Sum256(b)
		proofHash := hex.EncodeToString(h[:])
		txSig := "DEMO_" + proofHash[:44]

		c.JSON(http.StatusOK, gin.H{
			"proof_hash":    proofHash,
			"tx_signature":  txSig,
			"mode":          "demo",
			"message":       "Demo proof (no real Solana transaction)",
			"explorer_link": "https://solscan.io/tx/" + txSig + "?cluster=devnet",
		})
	}
}
