# Import necessary modules
from django.contrib.auth.tokens import PasswordResetTokenGenerator  # For generating password reset tokens
import six  # For compatibility with Python 2 and 3

# Custom token generator class
class tokengenerator(PasswordResetTokenGenerator):
    # Method to generate hash value for the token
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active))

# Instantiate the token generator
generate_token = tokengenerator()