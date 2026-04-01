from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class KYCStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    UNDER_REVIEW = 'under_review', _('Under Review')
    APPROVED = 'approved', _('Approved')
    REJECTED = 'rejected', _('Rejected')


class KYCProfileManager(models.Manager):
    """Custom manager for KYCProfile with common queries."""
    
    def submitted(self):
        """Get only KYC profiles that have been actually submitted (have ID/passport data)."""
        return self.exclude(id_number__isnull=True, id_number='')
    
    def pending(self):
        """Get all pending KYC profiles (for admin review)."""
        return self.filter(status=KYCStatus.PENDING)
    
    def by_email(self, email):
        """Get KYC profile by user email."""
        return self.filter(user__email=email).first()
    
    def approved(self):
        """Get all approved KYC profiles."""
        return self.filter(status=KYCStatus.APPROVED)
    
    def rejected(self):
        """Get all rejected KYC profiles."""
        return self.filter(status=KYCStatus.REJECTED)


class KYCProfile(models.Model):
    PROOF_CHOICES = [
        ('utility_bill', 'Utility Bill'),
        ('bank_statement', 'Bank Statement'),
        ('lease_agreement', 'Lease Agreement'),
        ('government_letter', 'Government Letter'),
        ('other', 'Other'),
    ]

    proof_of_address_type = models.CharField(
        max_length=50, 
        choices=PROOF_CHOICES, 
        blank=True, 
        null=True
    )
    proof_of_address_date = models.DateField(null=True, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='kyc_profile'
    )
    status = models.CharField(
        max_length=20,
        choices=KYCStatus.choices,
        default=KYCStatus.PENDING
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_kyc'
    )

    # Personal Information
    full_name = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    id_number = models.CharField(max_length=100, blank=True, unique=True, null=True)
    id_expiry_date = models.DateField(null=True, blank=True, help_text="ID/Passport expiry date")

    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # Documents (store file paths)
    id_document = models.FileField(upload_to='kyc/id_documents/', null=True, blank=True)
    selfie = models.FileField(upload_to='kyc/selfies/', null=True, blank=True)
    proof_of_address = models.FileField(upload_to='kyc/address_proofs/', null=True, blank=True , help_text="Utility bill, bank statement, lease agreement, etc.")

    notes = models.TextField(blank=True, help_text="Admin notes or rejection reason")

    objects = KYCProfileManager()

    class Meta:
        verbose_name = "KYC Profile"
        verbose_name_plural = "KYC Profiles"
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.email or self.user.username} - {self.status}"
    
    @property
    def user_email(self):
        """Convenience property to access user's email."""
        return self.user.email