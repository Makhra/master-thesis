from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from stamps.multiselect import MultiSelectField

CATALOG_CHOICES = (
    ('MI','Michel'),
    ('SC','Scott'),
    ('ST','Stanley Gibbons'),
    ('YV','Yvert et Tellier'),
    ('WA', 'WADP Numbering System'),
    ('SN', 'Stamp Number'),
    ('NO', 'None of the above'),
)

PAPER_CHOICES = (
    ('WO','Wove'),
    ('LA','Laid'),
    ('BA','Batonne'),
    ('PE','Pelure'),
    ('SI','Silk'),
    ('GR','Granite'),
    ('NO', 'None of the above'),
)

METHOD_CHOICES = (
    (0,'Engraving'),
    (1,'Typography'),
    (2,'Lithography'),
    (3,'Offset'),
    (4,'Recess'),
    (5, 'Letterset'),
    (6, 'Laserprint'),
    (7, 'Mezzotint'),
    (8, 'Photogravure'),
    (9, 'Collotype'),
    (10, 'Embossed'),
    (50, 'Other'),
)

FRIENDSHIP_CHOICES = (
    ('AC', 'Acquaintance'),
    ('FR', 'Friend'),
    ('PE', 'Pending'),
)

QUALITY_CHOICES = (
    ('MI', 'Mint'),
    ('US', 'Used'),
)
STATE_CHOICES = (
    ('PE', 'Pending'),
    ('AC', 'Accepted'),
    ('DO', 'Done'),
    ('RE', 'Reviewed'),
)
TRUST_CHOICES = (
    ('SC', 'Script addition'),
    ('US', 'User addition'),
)
# Create your models here.
class Stamp(models.Model):
    issue_country = models.CharField(max_length=65)
    issue_year = models.PositiveSmallIntegerField()
    face_value = models.CharField(max_length=65)
    currency = models.CharField(max_length=40, blank=True)
    paper_type = models.CharField(blank=True, max_length=65)
    printing_method = MultiSelectField(blank=True, max_length=18, choices=METHOD_CHOICES)
    name = models.CharField(max_length=65)
    series = models.CharField(max_length=65, blank=True)
    color = models.CharField(max_length=40, blank=True)
    watermark = models.CharField(max_length=40, blank=True)
    picture = models.ImageField(upload_to='up_stamps/', blank=True, db_index=True)
    perforation = models.CharField(max_length=40, blank=True)
    def __unicode__(self):
        return u'%i %s' % (self.stamp_id, self.catalogue_name)
class ImQuery(models.Model):
    up_stamp = models.ImageField(upload_to='temp/')
    
class ImList(models.Model):
    filename = models.CharField(max_length=100)
class ImWords(models.Model):
    stamp = models.ForeignKey(Stamp)
    wordid = models.CharField(max_length=100,db_index=True)
    vocname = models.CharField(max_length=100)

class ImHistograms(models.Model):
    stamp = models.ForeignKey(Stamp)
    histogram = models.TextField()
    vocname = models.CharField(max_length=100)


class StampInCatalog(models.Model):
    stamp = models.ForeignKey(Stamp)
    stampcat_id = models.CharField(max_length=15)
    catalog_name = models.CharField(max_length=40)
    trustability = models.CharField(max_length=2, choices=TRUST_CHOICES, default='US')
    class Meta:
        unique_together = ('stampcat_id', 'catalog_name')
        unique_together = ('stamp', 'catalog_name')

class UserProfil(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    location = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    grade = models.PositiveSmallIntegerField(default=0)
    transactions_amount = models.PositiveIntegerField(default=0)
    user_stamps = models.ManyToManyField(Stamp, through='Collection')
    user_contacts = models.ManyToManyField('self', symmetrical=False, through='ContactRelationship')

class ContactRelationship(models.Model):
    user = models.ForeignKey(UserProfil, related_name='from_contact')
    friend = models.ForeignKey(UserProfil, related_name='to_contact')
    type = models.CharField(max_length=2, choices=FRIENDSHIP_CHOICES, default='PE')
    date = models.DateField(auto_now=True)
    class Meta:
        unique_together = ('user', 'friend',)
    
class Collection(models.Model):
    user = models.ForeignKey(UserProfil)
    stamp = models.ForeignKey(Stamp)
    unused_quantity = models.PositiveSmallIntegerField(default=0)
    used_quantity = models.PositiveSmallIntegerField(default=0)
    modification_date = models.DateField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    class Meta:
        unique_together = ('user', 'stamp',)
    
class Interest(models.Model):
    interested_user = models.ForeignKey(UserProfil)
    collection = models.ForeignKey(Collection)
    quality = models.CharField(max_length=2, choices=QUALITY_CHOICES, default='US')
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default='PE')
    date_creation = models.DateField(auto_now=True)

class Transaction(models.Model):
    interest = models.OneToOneField(Interest, primary_key=True)
    grade_sender = models.PositiveSmallIntegerField(null=True)
    grade_receiver = models.PositiveSmallIntegerField(null=True)
    review_sender = models.TextField(validators=[MaxLengthValidator(450)], blank=True)
    review_receiver = models.TextField(validators=[MaxLengthValidator(450)], blank=True)

class Message(models.Model):
    sender = models.ForeignKey(UserProfil, related_name='sender')
    receiver = models.ForeignKey(UserProfil, related_name='receiver')
    message = models.TextField(validators=[MaxLengthValidator(500)])
    sent_time = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)


def create_user_profil(sender, instance, created, **kwargs):
    if created:
        profil, created = UserProfil.objects.get_or_create(user=instance)

post_save.connect(create_user_profil, sender=User)
