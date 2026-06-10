package com.example.stealthguard // You can change this to match your Android project's package

import android.graphics.BitmapFactory
import android.graphics.Color
import android.util.Base64
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.nio.ByteBuffer
import java.security.MessageDigest
import java.security.SecureRandom
import javax.crypto.Cipher
import javax.crypto.Mac
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.PBEKeySpec
import javax.crypto.spec.SecretKeySpec

object Steganography {

    private const val DELIMITER = "====EOF===="
    private val EOF_MARKER = "====STEALTHGUARD====".toByteArray(Charsets.UTF_8)
    private val SALT = "cybersecurity_salt".toByteArray(Charsets.UTF_8)

    /**
     * Generates a 32-byte key from password and salt using PBKDF2HMAC-SHA256
     * with 100,000 iterations, matching Python cryptography.hazmat's PBKDF2HMAC.
     */
    private fun generateRawKey(password: String): ByteArray {
        val factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
        val spec = PBEKeySpec(password.toCharArray(), SALT, 100000, 256)
        return factory.generateSecret(spec).encoded
    }

    /**
     * Encrypts a string message into a Python `cryptography.fernet` compatible token.
     */
    fun encryptMessage(message: String, password: String): String {
        val rawKey = generateRawKey(password)
        val signingKey = rawKey.copyOfRange(0, 16)
        val encryptionKey = rawKey.copyOfRange(16, 32)

        val secureRandom = SecureRandom()
        val iv = ByteArray(16)
        secureRandom.nextBytes(iv)

        val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
        cipher.init(Cipher.ENCRYPT_MODE, SecretKeySpec(encryptionKey, "AES"), IvParameterSpec(iv))
        val ciphertext = cipher.doFinal(message.toByteArray(Charsets.UTF_8))

        val timestamp = System.currentTimeMillis() / 1000L
        val version = 0x80.toByte()

        val dataToSign = ByteArrayOutputStream().apply {
            write(version.toInt())
            write(ByteBuffer.allocate(8).putLong(timestamp).array())
            write(iv)
            write(ciphertext)
        }.toByteArray()

        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(signingKey, "HmacSHA256"))
        val hmac = mac.doFinal(dataToSign)

        val fernetToken = ByteArrayOutputStream().apply {
            write(dataToSign)
            write(hmac)
        }.toByteArray()

        // Base64 URL-safe encoding without padding (matches Python's base64.urlsafe_b64encode)
        // Note: Python's fernet strips padding or expects standard URL safe base64, 
        // Android's NO_PADDING ensures compatibility.
        val tokenString = Base64.encodeToString(fernetToken, Base64.URL_SAFE or Base64.NO_WRAP)
        
        // Append delimiter like the Python backend
        return tokenString + DELIMITER
    }

    /**
     * Decrypts a Fernet token string.
     */
    fun decryptMessage(encryptedStr: String, password: String): String {
        var tokenStr = encryptedStr
        if (tokenStr.endsWith(DELIMITER)) {
            tokenStr = tokenStr.substring(0, tokenStr.length - DELIMITER.length)
        }

        val fernetToken = Base64.decode(tokenStr, Base64.URL_SAFE or Base64.NO_WRAP)
        
        if (fernetToken.size < 1 + 8 + 16 + 32) {
            throw IllegalArgumentException("Invalid token size")
        }

        val version = fernetToken[0]
        if (version != 0x80.toByte()) {
            throw IllegalArgumentException("Invalid version")
        }

        val iv = fernetToken.copyOfRange(9, 25)
        val ciphertext = fernetToken.copyOfRange(25, fernetToken.size - 32)
        val hmac = fernetToken.copyOfRange(fernetToken.size - 32, fernetToken.size)

        val dataToSign = fernetToken.copyOfRange(0, fernetToken.size - 32)

        val rawKey = generateRawKey(password)
        val signingKey = rawKey.copyOfRange(0, 16)
        val encryptionKey = rawKey.copyOfRange(16, 32)

        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(signingKey, "HmacSHA256"))
        val computedHmac = mac.doFinal(dataToSign)

        if (!MessageDigest.isEqual(hmac, computedHmac)) {
            throw IllegalArgumentException("Invalid password or corrupted data (signature mismatch).")
        }

        val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
        cipher.init(Cipher.DECRYPT_MODE, SecretKeySpec(encryptionKey, "AES"), IvParameterSpec(iv))
        val decryptedText = cipher.doFinal(ciphertext)

        return String(decryptedText, Charsets.UTF_8)
    }

    /**
     * Hides an encrypted message inside an image or audio file by appending to EOF.
     * Keeps file size practically the same.
     */
    fun encodeMedia(mediaPath: File, message: String, password: String, outputPath: File): Boolean {
        val encryptedMsg = encryptMessage(message, password)
        
        FileInputStream(mediaPath).use { inputStream ->
            FileOutputStream(outputPath).use { outputStream ->
                inputStream.copyTo(outputStream)
                outputStream.write(EOF_MARKER)
                outputStream.write(encryptedMsg.toByteArray(Charsets.UTF_8))
            }
        }
        return true
    }

    /**
     * Extracts and decrypts a hidden message from an image or audio file.
     */
    fun decodeMedia(mediaPath: File, password: String): String {
        val mediaBytes = mediaPath.readBytes()
        val markerIndex = indexOf(mediaBytes, EOF_MARKER)

        if (markerIndex != -1) {
            val encryptedBytes = mediaBytes.copyOfRange(markerIndex + EOF_MARKER.size, mediaBytes.size)
            try {
                val extractedText = String(encryptedBytes, Charsets.UTF_8)
                if (extractedText.contains(DELIMITER)) {
                    val encryptedMsg = extractedText.substringBefore(DELIMITER) + DELIMITER
                    return decryptMessage(encryptedMsg, password)
                }
            } catch (e: Exception) {
                // Fallback to LSB if EOF extraction fails
            }
        }

        // --- FALLBACK TO OLD LSB METHOD (IMAGES ONLY) ---
        return decodeMediaLsb(mediaPath, password)
    }

    /**
     * Helper function to find subarray index
     */
    private fun indexOf(array: ByteArray, target: ByteArray): Int {
        if (target.isEmpty()) return 0
        outer@ for (i in 0 until array.size - target.size + 1) {
            for (j in target.indices) {
                if (array[i + j] != target[j]) {
                    continue@outer
                }
            }
            return i
        }
        return -1
    }

    /**
     * Decodes a hidden message using the LSB method with Android's BitmapFactory.
     */
    private fun decodeMediaLsb(mediaPath: File, password: String): String {
        // BitmapFactory is the Android equivalent of PIL.Image
        val bitmap = BitmapFactory.decodeFile(mediaPath.absolutePath)
            ?: throw IllegalArgumentException("No hidden message found in this media file.")

        val width = bitmap.width
        val height = bitmap.height

        val binaryData = StringBuilder()
        val extractedText = StringBuilder()

        for (y in 0 until height) {
            for (x in 0 until width) {
                val pixel = bitmap.getPixel(x, y)
                
                // Extract RGB values
                val rgb = intArrayOf(Color.red(pixel), Color.green(pixel), Color.blue(pixel))
                
                // Extract LSB from R, G, B
                for (i in 0..2) {
                    binaryData.append(rgb[i] and 1)
                    
                    // Check every 8 bits
                    if (binaryData.length >= 8 && binaryData.length % 8 == 0) {
                        val byteStr = binaryData.substring(binaryData.length - 8)
                        extractedText.append(Integer.parseInt(byteStr, 2).toChar())
                        
                        // Check if we reached the delimiter
                        if (extractedText.toString().endsWith(DELIMITER)) {
                            val encryptedMsg = extractedText.toString().substringBefore(DELIMITER) + DELIMITER
                            return decryptMessage(encryptedMsg, password)
                        }
                    }
                }
            }
        }

        throw IllegalArgumentException("No hidden message found in this image.")
    }
}
