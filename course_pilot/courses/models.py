from django.db import models

class Programme(models.Model):
    programme_code = models.CharField(max_length=20, unique=True)
    programme_name = models.CharField(max_length=255)
    university = models.CharField(max_length=255)
    cluster_points = models.FloatField()
    
    def __str__(self):
        return f"{self.programme_name} - {self.university}"

class SubjectRequirement(models.Model):
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    subject_1 = models.CharField(max_length=100)
    grade_1 = models.CharField(max_length=5)
    subject_2 = models.CharField(max_length=100, blank=True, null=True)
    grade_2 = models.CharField(max_length=5, blank=True, null=True)
    subject_3 = models.CharField(max_length=100, blank=True, null=True)
    grade_3 = models.CharField(max_length=5, blank=True, null=True)
    subject_4 = models.CharField(max_length=100, blank=True, null=True)
    grade_4 = models.CharField(max_length=5, blank=True, null=True)
    
    def __str__(self):
        return f"Requirements for {self.programme.programme_name}"