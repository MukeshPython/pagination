import logging
from django.shortcuts import render
from rest_framework import views
from rest_framework import status
import requests
import random
import string
import concurrent.futures
from django.db import connection
import json
import time
from rest_framework.response import Response
from adrf.views import APIView
from rest_framework import generics
from . import serializers
from . import models
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class InsertPageApiData(views.APIView):
    def get(self, request):
        start = time.time()

        def insert_data(data):
            with connection.cursor() as cursor:
                api_data = data
                for item in api_data:
                    # api_id = generate_api_id()
                    raw_query = """
                                    INSERT INTO pagination (
                                        api_id, id, name, tagline, first_brewed, description, image_url, 
                                        abv, ibu, target_fg, target_og, ebc, srm, ph, attenuation_level, 
                                        volume, boil_volume, method, ingredients, food_pairing, 
                                        brewers_tips, contributed_by
                                    ) VALUES (
                                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                        %s, %s, %s, %s, %s, %s
                                    )
                                """
                    params = (
                        generate_api_id(),
                        item["id"],
                        item["name"],
                        item["tagline"],
                        item["first_brewed"],
                        item["description"],
                        item["image_url"],
                        item["abv"],
                        item["ibu"],
                        item["target_fg"],
                        item["target_og"],
                        item["ebc"],
                        item["srm"],
                        item["ph"],
                        item["attenuation_level"],
                        str(item["volume"]),
                        str(item["boil_volume"]),
                        str(item["method"]),
                        str(item["ingredients"]),
                        str(item["food_pairing"]),
                        item["brewers_tips"],
                        item["contributed_by"]
                    )

                    cursor.execute(raw_query, params)

        def generate_api_id():
            with connection.cursor() as cursor:
                api_id = "API" + "".join(random.choice(string.digits) for i in range(6))
                cursor.execute("SELECT api_id FROM pagination WHERE api_id=%s", (api_id,))
                db_id = cursor.fetchone()
                if not db_id:
                    return api_id
                else:
                    api_id = generate_api_id()
                    return api_id

        def fetch_data(url):
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for non-200 status codes
                data = response.json()
                insert_data(data)
                return {"message": "success"}
            except requests.exceptions.RequestException as e:
                return {'error': f'Failed to retrieve data from {url}: {str(e)}'}
            except json.JSONDecodeError as e:
                return {'error': f'Failed to parse JSON response from {url}: {str(e)}'}

        api_urls = ['https://api.punkapi.com/v2/beers/',
                    'https://api.punkapi.com/v2/beers/',
                    'https://api.punkapi.com/v2/beers/',
                    ]

        def page(url):
            for i in range(1, 11):
                api_url = str(url) + str(i)
                fetch_data(api_url)

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(api_urls)) as executor:
            results = [executor.submit(page, url) for url in api_urls]
            concurrent.futures.wait(results)
        end = time.time()
        tot = end - start
        val = {"total": tot, "data": "Data inserted successfully"}

        return Response(val, status=status.HTTP_201_CREATED)


import nest_asyncio
import asyncio
import aiomysql
import httpx
import random
import string

from rest_framework import status


# class Asyncio(APIView):
#     async def get(self, request):
#         # Initialize the database connection pool
#         async with aiomysql.create_pool(
#                 host='localhost',
#                 user='root',
#                 password='vrdella!6',
#                 db='thread',
#                 port=3306,
#                 minsize=1,  # Adjust the pool size as needed
#                 maxsize=5,
#         ) as pool:
#             start = time.time()
#
#             async def insert_data(conn, data):
#                 try:
#                     async with conn.cursor() as cursor:
#                         api_data = data
#                         # cursor = connection.cursor()
#                         for item in api_data:
#                             raw_query = """INSERT INTO pagination (api_id, id, name, tagline, first_brewed, description, image_url, abv, ibu, target_fg, target_og, ebc, srm, ph, attenuation_level, volume, boil_volume, method, ingredients, food_pairing, brewers_tips, contributed_by) VALUES (
#                                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)"""
#                             params = (
#                                 await generate_api_id(conn),
#                                 item["id"],
#                                 item["name"],
#                                 item["tagline"],
#                                 item["first_brewed"],
#                                 item["description"],
#                                 item["image_url"],
#                                 item["abv"],
#                                 item["ibu"],
#                                 item["target_fg"],
#                                 item["target_og"],
#                                 item["ebc"],
#                                 item["srm"],
#                                 item["ph"],
#                                 item["attenuation_level"],
#                                 str(item["volume"]),
#                                 str(item["boil_volume"]),
#                                 str(item["method"]),
#                                 str(item["ingredients"]),
#                                 str(item["food_pairing"]),
#                                 item["brewers_tips"],
#                                 item["contributed_by"])
#                             await cursor.execute(raw_query, params)
#                 except Exception as e:
#                     return Response(str(e))
#
#             async def generate_api_id(conn):
#                 async with conn.cursor() as cursor:
#                     api_id = "API" + "".join(random.choice(string.digits) for _ in range(5))
#                     await cursor.execute("SELECT api_id FROM pagination WHERE api_id=%s", (api_id,))
#                     db_id = cursor.fetchone()
#                     if not db_id:
#                         return api_id
#                     else:
#                         api_id = await generate_api_id(conn)
#                         return api_id
#                     #
#
#             async def fetch_data(url, conn):
#                 try:
#                     async with httpx.AsyncClient() as client:
#                         response = await client.get(url)
#                         if response.status_code == 200:
#                             data = response.json()
#                             async with pool.acquire() as conn:
#                                 await insert_data(conn, data)
#                             return {"message": "success"}
#                         else:
#                             return {'error': f'Failed to retrieve data from {url}'}
#                 except Exception as e:
#                     return {'error': f'Error while fetching data from {url}: {str(e)}'}
#
#             api_urls = ['https://api.punkapi.com/v2/beers/',
#                         'https://api.punkapi.com/v2/beers/',
#                         'https://api.punkapi.com/v2/beers/', ]
#
#             async def page(url, conn):
#                 for i in range(1, 11):
#                     await fetch_data(f'{url}{i}', conn)
#
#             # Use a connection from the pool for each URL
#             async with pool.acquire() as conn:
#                 results = await asyncio.gather(*[page(api_url, conn) for api_url in api_urls])
#
#             end = time.time()
#             total_time = end - start
#             response_data = {"total": total_time, "data": "Data inserted successfully"}
#             return Response(response_data, status=status.HTTP_201_CREATED)


# class InsertPageApiKeyData(views.APIView):
#     def get(self, request):
#         start = time.time()
#
#         def generate_api_id():
#             with connection.cursor() as cursor:
#                 api_id = "API" + "".join(random.choice(string.digits) for i in range(6))
#                 cursor.execute("SELECT api_id FROM pagination WHERE api_id=%s", (api_id,))
#                 db_id = cursor.fetchone()
#                 if not db_id:
#                     return api_id
#                 else:
#                     api_id = generate_api_id()
#                     return api_id
#
#         def insert_data(data):
#             with connection.cursor() as cursor:
#                 api_data = data['data']
#                 for item in api_data:
#                     print(item)
#                     print(len(api_data))
#                     # api_id = generate_api_id()
#                     raw_query = """INSERT INTO key(id, state, country, type, pst, hst, gst, combined_rate, start)
#                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
#                     params = (
#                         generate_api_id(),
#                         item["state"],
#                         item["country"],
#                         item["type"],
#                         str(item["pst"]),
#                         str(item["hst"]),
#                         str(item["gst"]),
#                         str(item["combined_rate"]),
#                         item["start"],
#                     )
#                     cursor.execute(raw_query, params)
#
#         def fetch_data(url):
#             try:
#                 headers = {
#                     "apikey": "W33I9HTI8ZgdjpAdA0rbQbn9DnawoTX9"
#                 }
#                 response = requests.get(url, headers=headers)
#                 response.raise_for_status()  # Raise an exception for non-200 status codes
#                 data = response.json()
#                 insert_data(data)
#                 return {"message": "success"}
#             except requests.exceptions.RequestException as e:
#                 return {'error': f'Failed to retrieve data from {url}: {str(e)}'}
#             except json.JSONDecodeError as e:
#                 return {'error': f'Failed to parse JSON response from {url}: {str(e)}'}
#
#         api_urls = ["https://api.apilayer.com/tax_data/canada_rate_list",
#                     # "https://api.apilayer.com/tax_?data/canada_rate_list",
#                     # "https://api.apilayer.com/tax_data/canada_rate_list"
#                     ]
#
#         with concurrent.futures.ThreadPoolExecutor(max_workers=len(api_urls)) as executor:
#             results = [executor.submit(fetch_data, url) for url in api_urls]
#             # concurrent.futures.wait(results)
#
#             end = time.time()
#             total_time = end - start
#             data1 = {"data": results[0]['data'], "time": total_time}
#             return Response(data1, status=status.HTTP_201_CREATED)

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
class Getdata(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = serializers.paginationserializer
    queryset = models.Pagination.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            user = User.objects.get(username='mukesh')
            # Token.objects.create(user=user)
            data = models.Pagination.objects.all()
            serializer = serializers.paginationserializer(instance=data, many=True)
            data = serializer.data
            return Response(data)
        except Exception as e:
            return Response(str(e))


class InsertPageApiKeyData(views.APIView):
    def get(self, request):
        def insert_data(data):
            with connection.cursor() as cursor:
                api_data = data['data']
                for item in api_data:
                    # api_id = generate_api_id()
                    raw_query = """INSERT INTO key (
                     id, state, country, type, pst, hst, gst, combined_rate, start
                     ) VALUES (
                     %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    params = (
                        generate_api_id(),
                        item["state"],
                        item["country"],
                        item["type"],
                        str(item["pst"]),
                        str(item["hst"]),
                        str(item["gst"]),
                        str(item["combined_rate"]),
                        item["start"],
                    )
                    cursor.execute(raw_query, params)

        def generate_api_id():
            with connection.cursor() as cursor:
                id = "API" + "".join(random.choice(string.digits) for i in range(5))
                cursor.execute("SELECT id FROM pagination WHERE id=%s", (id,))
                db_id = cursor.fetchone()
                if not db_id:
                    return id
                else:
                    id = generate_api_id()
                    return id
        #

        api_urls = ["https://api.apilayer.com/tax_data/canada_rate_list"]
                    # "https://api.apilayer.com/tax_data/canada_rate_list",
                    # "https://api.apilayer.com/tax_data/canada_rate_list"]

        def fetch_data(url):
            headers = {
                "apikey": "W33I9HTI8ZgdjpAdA0rbQbn9DnawoTX9"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            insert_data(response.json())
            return response.json()

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(api_urls)) as executor:
            results = list(executor.map(fetch_data, api_urls))
            # concurrent.futures.wait(results)
        data=[ result for result in results]
        return Response({"data": data}, status=status.HTTP_201_CREATED)


class InsertData(views.APIView):
    def get(self, request):
        start = time.time()

        def insert_data(data):
            with connection.cursor() as cursor:
                api_data = data
                for item in api_data:
                    # api_id = generate_api_id()
                    print(item)
                    raw_query = """
                                    INSERT INTO paginationt_app_apikey (
                                        api_id, id, name, tagline, first_brewed, description, image_url, 
                                        abv, ibu, target_fg, target_og, ebc, srm, ph, attenuation_level, 
                                        volume, boil_volume, method, ingredients, food_pairing, 
                                        brewers_tips, contributed_by
                                    ) VALUES (
                                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                        %s, %s, %s, %s, %s, %s
                                    )
                                """
                    params = (
                        item['api_id'],
                        item["id"],
                        item["name"],
                        item["tagline"],
                        item["first_brewed"],
                        item["description"],
                        item["image_url"],
                        item["abv"],
                        item["ibu"],
                        item["target_fg"],
                        item["target_og"],
                        item["ebc"],
                        item["srm"],
                        item["ph"],
                        item["attenuation_level"],
                        str(item["volume"]),
                        str(item["boil_volume"]),
                        str(item["method"]),
                        str(item["ingredients"]),
                        str(item["food_pairing"]),
                        item["brewers_tips"],
                        item["contributed_by"]
                    )

                    cursor.execute(raw_query, params)

        def fetch_data(url):
            try:
                headers = {
                    "Authorization": "Token 2b65ba33103cb842999268dac0ad4658eb55ddc6"
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise an exception for non-200 status codes
                data = response.json()
                insert_data(data)
                return {"message": "success"}
            except requests.exceptions.RequestException as e:
                return {'error': f'Failed to retrieve data from {url}: {str(e)}'}
            except json.JSONDecodeError as e:
                return {'error': f'Failed to parse JSON response from {url}: {str(e)}'}

        api_urls = ['http://127.0.0.1:8000/get/',
                    'http://127.0.0.1:8000/get/',
                    'http://127.0.0.1:8000/get/',
                    ]
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(api_urls)) as executor:
            results = list(executor.map(fetch_data, api_urls))
            # concurrent.futures.wait(results)
        data = [result for result in results]
        end = time.time()
        tot = end - start
        # val = {"total": tot, "data": "Data inserted successfully"}

        return Response(data, status=status.HTTP_201_CREATED)
