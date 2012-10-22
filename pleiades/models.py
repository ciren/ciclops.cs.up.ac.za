from django.db import models

# Create your models here.

# User model
class user(models.Model):
	name = models.CharField(max_length=50)
	password = models.CharField(max_length=200)
	lolipops = models.IntegerField()

	def __unicode__(self):
		return self.name
