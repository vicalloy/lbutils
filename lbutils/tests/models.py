from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=255)
    descn = models.TextField(blank=True)
    price = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    category = models.ForeignKey(
        Category, null=True, blank=True,
        on_delete=models.SET_NULL
    )
    authors = models.ManyToManyField(Author, blank=True)

    class Meta:
        ordering = ["name"]
        permissions = (
            ("sft_mgr_book", "manager book"),
        )

    def __str__(self):
        return self.name
