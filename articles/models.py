from django.db import models
from django.urls import reverse


class Articles(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={"pk": self.pk})





class Comment(models.Model):  # new


    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    comment = models.CharField(max_length=140)
    author = models.CharField(max_length=100)

    def __str__(self):
        return self.comment


    def get_absolute_url(self):
        return reverse("article_list")
