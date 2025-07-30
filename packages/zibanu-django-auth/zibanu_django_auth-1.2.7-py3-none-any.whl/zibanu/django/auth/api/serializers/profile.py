# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2024. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2024. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         27/04/23 6:58
# Project:      Zibanu - Django
# Module Name:  profile
# Description:
# ****************************************************************
from django.conf import settings

from zibanu.django.rest_framework import serializers
from zibanu.django.auth.models import UserProfile


class ProfileSerializer(serializers.ModelSerializer):
    """
    UserProfile entity serializer.
    """

    class Meta:
        """
        ProfileSerializer Metaclass
        """
        model = UserProfile
        fields = (
            "timezone", "theme", "lang", "messages_timeout", "keep_logged_in", "multiple_login", "secure_password"
        )


class ProfileExtendedSerializer(ProfileSerializer):
    """
    UserProfile entity extended serializer to include avatar.
    """
    width = settings.ZB_AUTH_AVATAR_SIZE
    height = settings.ZB_AUTH_AVATAR_SIZE
    represent_in_base64 = settings.ZB_AUTH_AVATAR_BASE64
    avatar = serializers.HybridImageField(max_length=None, required=False, allow_null=False,
                                          represent_in_base64=represent_in_base64, image_width=width,
                                          image_height=height)

    class Meta:
        """
        ProfileSerializer Metaclass
        """
        model = UserProfile
        fields = (
            "timezone", "theme", "lang", "avatar", "messages_timeout", "keep_logged_in", "app_settings",
            "multiple_login", "secure_password"
        )
