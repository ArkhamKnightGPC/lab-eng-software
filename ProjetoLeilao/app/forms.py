import decimal
from django import forms
from datetime import datetime
import pytz
from django.template import Context, Template

from . import models

class LoteCreateForm(forms.ModelForm): #Ofertar lote de produtos
    class Meta:
        model = models.Lote
        fields = ('nome', 'descricao', 'estado_conservacao', 'autor', 'editora', 'numero_de_paginas', 'valor_reserva', 'cliente_vendedor', 'data_final')
        widgets = { #elementos HTML correspondentes aos campos
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'estado_conservacao': forms.Select(attrs={'class': 'form-control'}),
            'autor': forms.TextInput(attrs={'class': 'form-control'}),
            'editora': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_de_paginas': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_reserva': forms.NumberInput(attrs={'class': 'form-control'}),
            'cliente_vendedor': forms.TextInput(attrs={'class': 'form-control', 'value': '', 'id': 'cliente_vendedor_field', 'type': 'hidden'}),
            'data_final': forms.DateTimeInput(attrs={'class': 'form-control'}),
        }
    def clean(self):
        #vamos calcular taxa de comissao a ser paga
        valor_base = self.cleaned_data['valor_reserva']
        if(valor_base <= 1000):
            self.instance.taxa_comissao = float(valor_base) / 100.00 # taxa de 1%
        elif(valor_base <= 10000):
            self.instance.taxa_comissao = 2 * float(valor_base) / 50.00 # taxa de 2%
        elif(valor_base <= 50000):
            self.instance.taxa_comissao = 3 * float(valor_base) / 100.00  # taxa de 3%
        elif(valor_base <= 100000):
            self.instance.taxa_comissao = 4 * float(valor_base) / 100.00  # taxa de 4%
        else:
            self.instance.taxa_comissao = 5 * float(valor_base) / 100.00  # taxa de 5%
        #PRIMEIRA VALIDACAO: Leilao precisa acabar no futuro
        utc = pytz.UTC
        tempo_atual = utc.localize(datetime.now())
        self.instance.data_inicio = tempo_atual
        tempo_final = self.cleaned_data['data_final']
        if (tempo_final < tempo_atual):
            raise forms.ValidationError('O leilão não pode acabar antes do momento atual!')
        #SEGUNDA VALIDACAO: Vendedor tem saldo para pagar taxa de comissao
        saldo_vendedor = models.Saldo.objects.all().get(username_cliente = self.cleaned_data['cliente_vendedor'])
        if(saldo_vendedor.valor < self.instance.taxa_comissao):
            raise forms.ValidationError('Seu saldo de ' + str(saldo_vendedor.valor) + ' não é suficiente para pagar a taxa de comissão ' + str(self.instance.taxa_comissao))

class LoteFinalizarLeilaoForm(forms.ModelForm): #Hora de realizar cobranças
    class Meta:
        model = models.Lote
        fields = ('leilao_finalizado',)
        widgets = {
            'leilao_finalizado': forms.CheckboxInput(),
        }
    def clean(self):
        #PRIMEIRA VALIDACAO: Data final precisa estar no passado
        utc = pytz.UTC
        tempo_atual = utc.localize(datetime.now())
        tempo_final = self.instance.data_final
        if(tempo_final > tempo_atual):
            raise forms.ValidationError("O leilão ainda vai acabar:" + tempo_final.strftime("%m/%d/%Y, %H:%M:%S"))
        if(self.instance.valor_lance_mais_alto >= self.instance.valor_reserva): #vamos realizar venda
            # valor total a ser pago = lance + taxa de comissao!!
            valor_lance = self.instance.valor_lance_mais_alto
            valor_comissao = 0
            if (valor_lance <= 1000):
                valor_comissao = 3 * float(valor_lance) / 100.00  # taxa de 3%
            elif (valor_lance <= 10000):
                valor_comissao = 4 * float(valor_lance) / 50.00  # taxa de 4%
            elif (valor_lance <= 50000):
                valor_comissao = 5 * float(valor_lance) / 100.00  # taxa de 5%
            elif (valor_lance <= 100000):
                valor_comissao = 6 * float(valor_lance) / 100.00  # taxa de 6%
            else:
                valor_comissao = 7 * float(valor_lance) / 100.00  # taxa de 7%
            valor_total = valor_lance + decimal.Decimal(valor_comissao)
            saldo_comprador = models.Saldo.objects.all().get(
                username_cliente=self.instance.cliente_comprador_lance_mais_alto.username)
            # ok, vamos descontar valor total a ser pago do saldo
            saldo_comprador.valor = saldo_comprador.valor - decimal.Decimal(valor_total)
            saldo_comprador.save()
            # ok, vamos adicionar pagamento ao leilao
            pagamento = models.Pagamento(lote=self.instance, data=tempo_atual, valor=valor_comissao, tipo_de_pagamento='COMISSÃO LANCE')
            pagamento.save()
            # ok, vamos adicionar saldo ao vendedor
            saldo_vendedor = models.Saldo.objects.all().get(username_cliente=self.instance.cliente_vendedor.username)
            saldo_vendedor.valor = saldo_vendedor.valor + valor_lance
            saldo_vendedor.save()
        self.instance.save()

class LoteLiberarForm(forms.ModelForm): #Leiloeiro libera lote para lances
    class Meta:
        model = models.Lote
        fields = ('liberado_para_lances', 'valor_minimo_lance', 'valor_minimo_incremento_por_lance')
        widgets = {
            'liberado_para_lances': forms.CheckboxInput(),
            'valor_minimo_lance': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_minimo_incremento_por_lance': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    def clean(self):
        #PRIMEIRA VALIDACAO: Precisa ter liberado lote
        lote_liberado = self.cleaned_data['liberado_para_lances']
        if(lote_liberado == False):
            raise forms.ValidationError('Para enviar esse formulário, você precisa liberar o lote para leilão')
        saldo_vendedor = models.Saldo.objects.all().get(username_cliente=self.instance.cliente_vendedor)
        # ok, vamos descontar taxa de comissao do saldo
        saldo_vendedor.valor -= decimal.Decimal(self.instance.taxa_comissao)
        saldo_vendedor.save()
        # ok, vamos adicionar pagamento ao leilao
        utc = pytz.UTC
        tempo_atual = utc.localize(datetime.now())
        pagamento = models.Pagamento(lote=self.instance, data=tempo_atual, valor=self.instance.taxa_comissao, tipo_de_pagamento='COMISSÃO NOVO LOTE')
        pagamento.save()

class LoteEditarForm(forms.ModelForm): #Editar dados do lote

    class Meta:
        model = models.Lote
        fields = ('nome', 'descricao', 'estado_conservacao', 'autor', 'editora', 'numero_de_paginas')
        widgets = {  # elementos HTML correspondentes aos campos
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'estado_conservacao': forms.Select(attrs={'class': 'form-control'}),
            'autor': forms.TextInput(attrs={'class': 'form-control'}),
            'editora': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_de_paginas': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LoteEditarAdmForm(forms.ModelForm): #Editar dados do lote (Leiloeiro)

    class Meta:
        model = models.Lote
        fields = ('nome', 'descricao', 'estado_conservacao', 'autor', 'editora', 'numero_de_paginas', 'valor_minimo_incremento_por_lance')
        widgets = {  # elementos HTML correspondentes aos campos
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'estado_conservacao': forms.Select(attrs={'class': 'form-control'}),
            'autor': forms.TextInput(attrs={'class': 'form-control'}),
            'editora': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_de_paginas': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_minimo_incremento_por_lance': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class LoteUpdateForm(forms.ModelForm): #Realizar Lance

    cliente_comprador_username = forms.CharField(max_length = 150, widget=forms.HiddenInput(
                attrs={'class': 'form-control', 'value': '', 'id': 'cliente_comprador_username_field', 'type': 'hidden', 'is_required':'True'}))

    class Meta:
        model = models.Lote
        fields = ('valor_lance_mais_alto', 'cliente_comprador_lance_mais_alto')
        widgets = {
            'valor_lance_mais_alto': forms.NumberInput(attrs={'class': 'form-control'}),
            'cliente_comprador_lance_mais_alto': forms.TextInput(
                attrs={'class': 'form-control', 'value': '', 'id': 'cliente_comprador_lance_mais_alto_field', 'type': 'hidden'}),
        }
    def clean(self):
        #PRIMEIRA VALIDACAO: Tem que ser maior que lance atual
        lance_formulario = self.cleaned_data['valor_lance_mais_alto']
        lance_atual = self.instance.valor_lance_mais_alto
        if( lance_formulario < lance_atual):
            raise forms.ValidationError('Você precisa oferecer mais que o lance mais alto atual (' + str(lance_atual) + ')')
        #SEGUNDA VALIDACAO: Tem que ser maior que lance minimo
        lance_minimo = self.instance.valor_minimo_lance
        if(lance_formulario < lance_minimo):
            raise forms.ValidationError('O valor mínimo de lance para esse lote eh ' + str(lance_minimo))
        #TERCEIRA VALIDACAO: Se ja teve lance, precisa respeitar incremento minimo
        incremento_minimo = self.instance.valor_minimo_incremento_por_lance
        if(lance_atual >= lance_minimo and lance_formulario < lance_atual + incremento_minimo):
            raise forms.ValidationError('Pela regra de incremento mínimo, você precisa ofertar pelo menos ' + str(lance_atual+incremento_minimo))
        #QUARTA VALIDACAO: Se o leilao ja expirou, nao dah pra fazer lance
        utc = pytz.UTC
        tempo_atual = utc.localize(datetime.now())
        tempo_final = self.instance.data_final
        if( tempo_final < tempo_atual ):
            raise forms.ValidationError('Infelizmente esse leilão acabou na datetime ' + tempo_final.strftime("%m/%d/%Y, %H:%M:%S"))
        # valor total a ser pago = lance + taxa de comissao!!
        valor_lance = self.cleaned_data['valor_lance_mais_alto']
        valor_comissao = 0
        if (valor_lance <= 1000):
            valor_comissao = 3 * float(valor_lance) / 100.00  # taxa de 3%
        elif (valor_lance <= 10000):
            valor_comissao = 4 * float(valor_lance) / 50.00  # taxa de 4%
        elif (valor_lance <= 50000):
            valor_comissao = 5 * float(valor_lance) / 100.00  # taxa de 5%
        elif (valor_lance <= 100000):
            valor_comissao = 6 * float(valor_lance) / 100.00  # taxa de 6%
        else:
            valor_comissao = 7 * float(valor_lance) / 100.00  # taxa de 7%
        valor_total = valor_lance + decimal.Decimal(valor_comissao)
        #QUINTA VALIDACAO: Comprador precisar ter saldo suficiente
        saldo_comprador = models.Saldo.objects.all().get(username_cliente = self.cleaned_data['cliente_comprador_username'])
        if(saldo_comprador.valor < valor_total):
            raise forms.ValidationError('Seu saldo de ' + str(saldo_comprador.valor) + ' não é suficiente para pagar o valor total ' + str(valor_total))
        #ok, vamos incrementar numero de lances do lote
        self.instance.numero_de_lances = self.instance.numero_de_lances + 1
        self.instance.save()

class saldoUpdateForm(forms.ModelForm): #Atualizar saldo
    class Meta:
        model = models.Saldo
        fields = ('username_cliente', 'valor')
        widgets = {
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'username_cliente': forms.TextInput(
                attrs={'class': 'form-control', 'value': '', 'id': 'username_cliente_field', 'type': 'hidden'}),
        }
    def clean(self):
        valor_formulario = self.cleaned_data['valor']
        username_cliente_formulario = self.cleaned_data['username_cliente']
        saldo_cliente = models.Saldo.objects.all().get(username_cliente=username_cliente_formulario)
        saldo_cliente.valor = valor_formulario
        saldo_cliente.save()

data_inicio_relatorio = None
data_final_relatorio = None

class gerarRelatorioFaturamento(forms.Form):
    # filtrar pagamentos realizados entre certas datas
    data_inicio = forms.DateTimeField(widget = forms.DateTimeInput())
    data_final = forms.DateTimeField(widget = forms.DateTimeInput())

    def clean(self):
        # PRIMEIRA VALIDACAO: data inicio precisa ser menor que data final
        if(self.cleaned_data['data_inicio'] > self.cleaned_data['data_final']):
            raise forms.ValidationError('Datas inseridas são inválidas')
        global data_inicio_relatorio
        data_inicio_relatorio = self.cleaned_data['data_inicio']
        global data_final_relatorio
        data_final_relatorio = self.cleaned_data['data_final']

class gerarRelatorioDesempenho(forms.Form):
    # estatisticas de ofertas convertidas em vendas
    data_inicio = forms.DateTimeField(widget=forms.DateTimeInput())
    data_final = forms.DateTimeField(widget=forms.DateTimeInput())

    def clean(self):
        # PRIMEIRA VALIDACAO: data inicio precisa ser menor que data final
        if (self.cleaned_data['data_inicio'] > self.cleaned_data['data_final']):
            raise forms.ValidationError('Datas inseridas são inválidas')
        global data_inicio_relatorio
        data_inicio_relatorio = self.cleaned_data['data_inicio']
        global data_final_relatorio
        data_final_relatorio = self.cleaned_data['data_final']
