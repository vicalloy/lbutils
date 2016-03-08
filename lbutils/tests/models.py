# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)


class Book(models.Model):
    name = models.CharField(max_length=255)
    descn = models.TextField(blank=True)
    price = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    category = models.ForeignKey(Category, null=True, blank=True)

    class Meta:
        ordering = ["name"]
        permissions = (
            ("sft_mgr_book", "manager book"),
        )

    def __unicode__(self):
        return self.name
