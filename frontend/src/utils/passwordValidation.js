/**
 * Password validation utility.
 *
 * Requirements (matches backend):
 *   - Minimum 8 characters
 *   - At least one uppercase letter
 *   - At least one lowercase letter
 *   - At least one number
 */

export function validatePassword(password) {
  const errors = [];

  if (password.length < 8) {
    errors.push("Password must be at least 8 characters long");
  }
  if (!/[A-Z]/.test(password)) {
    errors.push("Password must contain at least one uppercase letter");
  }
  if (!/[a-z]/.test(password)) {
    errors.push("Password must contain at least one lowercase letter");
  }
  if (!/[0-9]/.test(password)) {
    errors.push("Password must contain at least one number");
  }

  return { valid: errors.length === 0, errors };
}

/**
 * Calculate password strength as a percentage (0-100).
 */
export function getPasswordStrength(password) {
  let score = 0;
  if (password.length >= 8) score += 25;
  if (password.length >= 12) score += 10;
  if (/[A-Z]/.test(password)) score += 20;
  if (/[a-z]/.test(password)) score += 20;
  if (/[0-9]/.test(password)) score += 15;
  if (/[^A-Za-z0-9]/.test(password)) score += 10;
  return Math.min(score, 100);
}

/**
 * Get a label and color class for the password strength.
 */
export function getStrengthLabel(strength) {
  if (strength < 30) return { label: "Weak", color: "bg-rose-500" };
  if (strength < 60) return { label: "Fair", color: "bg-amber-500" };
  if (strength < 80) return { label: "Good", color: "bg-yellow-400" };
  return { label: "Strong", color: "bg-emerald-500" };
}
