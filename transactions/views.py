from django.shortcuts import render,get_object_or_404

from rest_framework.views import APIView
from rest_framework import authentication,permissions
from rest_framework.response import Response

from transactions.models import Expense
from transactions.serializers import ExpenseSerializers
# Create your views here.
class ExpenseListCreateView(APIView):

    #authentication_classes=[authentication.BasicAuthentication]
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]


    def get(self,request):


        auth_user=request.user

        qs=Expense.objects.filter(owner=auth_user)

        serialiser_instance=ExpenseSerializers(qs,many=True)

        return Response(serialiser_instance.data)

    def post(self,request):

        form_data=request.data

        auth_user=request.user

        serializer_instance=ExpenseSerializers(data=form_data)

        if serializer_instance.is_valid():

            serializer_instance.save(owner=auth_user)
            return Response(serializer_instance.data)
        else:
             return Response (serializer_instance.errors)
        
from transactions.permissions import IsOwner
class ExpenseRetrieveUpdateDeleteView(APIView):
     #authentication_classes=[authentication.BasicAuthentication]
     authentication_classes=[authentication.TokenAuthentication]
     permission_classes=[IsOwner]

     def get(self,request,pk=None):
        #qs=Expense.objects.get(id=pk)
        qs=get_object_or_404(Expense,id=pk)

        self.check_object_permissions(request,qs)

        serialized_instance=ExpenseSerializers(qs)
        return Response(serialized_instance.data)        

     def put(self,request,pk=None):
         instance=get_object_or_404(Expense,id=pk)
         self.check_object_permissions(request,instance)

         form_data=request.data
         serialized_instance=ExpenseSerializers(data=form_data,instance=instance)

         if serialized_instance.is_valid():
             serialized_instance.save()
             return Response(data=serialized_instance.data)

         else:
             return Response(data=serialized_instance.errors)

     def delete(self,request,pk=None):
         qs=get_object_or_404(Expense,id=pk)
         self.check_object_permissions(request,qs)
         qs.delete()
         return Response({"message":"deleted..."})    

from datetime import datetime
from django.db.models import Sum

class ExpenseSummaryView(APIView):


    #authentication_classes =[authentication.BasicAuthentication]
    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAuthenticated]

    def get(self,request):

        auth_user_expenses = Expense.objects.filter(owner=request.user)

        response_data={
            "todays_total":0,
            "monthly_total":0
        }
         #todays_total

        cur_date = datetime.today().date()

        todays_total=auth_user_expenses.filter(
                                                created_at__date = cur_date
                                                ).values("amount").aggregate(total=Sum("amount")).get("total")

       

        response_data["todays_total"]= todays_total

        #monthly_total

        cur_month=datetime.today().month
        cur_year=datetime.today().year

        monthly_total=auth_user_expenses.filter(
            created_at__month=cur_month,created_at__year=cur_year).values("amount").aggregate(total=Sum("amount")).get("total")

        response_data["monthly_total"]=monthly_total
             

        return Response(response_data)
     