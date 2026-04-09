from django.core.management.base import BaseCommand
from apps.users.models import CustomUser
from apps.warehouses.models import Warehouse
from apps.products.models import Category, Unit, Product
from apps.batches.models import Batch
from apps.invoices.models import ShotInvoice
from apps.orders.models import Order, OrderItem, OrderStatusHistory
from apps.notifications.models import Notification
from apps.suppliers.models import Supplier
from apps.objects.models import ConstructionObject, ObjectMaterial, ObjectExpense
from apps.transfers.models import Transfer, TransferItem
from apps.estimates.models import Estimate, EstimateItem
from apps.payments.models import Payment
from datetime import date, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Seed database with realistic Uzbek warehouse data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # --- Units ---
        units_data = [
            ('Kilogram', 'kg'), ('Dona', 'ta'), ('Litr', 'l'),
            ('Metr', 'm'), ('Kvadrat metr', 'm²'), ('Tonna', 't'),
            ('Paket', 'pkt'), ('Quti', 'qut'),
        ]
        units = {}
        for name, abbr in units_data:
            u, _ = Unit.objects.get_or_create(name=name, defaults={'abbreviation': abbr})
            units[abbr] = u
        self.stdout.write(f'  Units: {len(units)}')

        # --- Categories ---
        cats_data = [
            ('Metall buyumlar', 'Armatura, profil, sim va boshqa metall mahsulotlar'),
            ('Qurilish materiallari', 'Sement, qum, shag\'al, g\'isht va boshqalar'),
            ('Elektr jihozlari', 'Kabel, rozetka, avtomat va boshqa elektr materiallari'),
            ('Sanitariya-texnika', 'Truba, kran, unitaz va boshqa santexnika'),
            ('Bo\'yoq va kimyoviy', 'Bo\'yoqlar, laklar, erituvchilar'),
            ('Yog\'och materiallari', 'Taxta, faner, brus va boshqalar'),
        ]
        cats = {}
        for name, desc in cats_data:
            c, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
            cats[name] = c
        self.stdout.write(f'  Categories: {len(cats)}')

        # --- Warehouses ---
        admin = CustomUser.objects.filter(role='ADMIN').first()
        wh_data = [
            ('Katta ombor (Markaziy)', 'Toshkent sh., Chilanzar tumani, Bunyodkor ko\'chasi 12', 10000),
            ('Kichik ombor #1 (Sergeli)', 'Toshkent sh., Sergeli tumani, Qo\'yliq ko\'chasi 45', 3000),
            ('Kichik ombor #2 (Olmazor)', 'Toshkent sh., Olmazor tumani, Universitet ko\'chasi 8', 2500),
            ('Samarqand filiali', 'Samarqand sh., Registon ko\'chasi 100', 5000),
        ]
        warehouses = []
        for name, addr, cap in wh_data:
            w, _ = Warehouse.objects.get_or_create(
                name=name,
                defaults={'address': addr, 'capacity': cap, 'responsible_user': admin, 'is_active': True}
            )
            warehouses.append(w)
        self.stdout.write(f'  Warehouses: {len(warehouses)}')

        # --- Users ---
        users_data = [
            ('+998901112233', 'Bobur', 'Karimov', 'KATTA_OMBOR_ADMINI', None, 'katta@matrix.uz'),
            ('+998902223344', 'Sherzod', 'Toshmatov', 'KICHIK_OMBOR_ADMINI', warehouses[1], 'sherzod@matrix.uz'),
            ('+998903334455', 'Dilshod', 'Rahimov', 'KICHIK_OMBOR_ADMINI', warehouses[2], 'dilshod@matrix.uz'),
            ('+998904445566', 'Malika', 'Usmanova', 'HISOBCHI', None, 'malika@matrix.uz'),
            ('+998905556677', 'Jasur', 'Aliyev', 'KICHIK_OMBOR_ADMINI', warehouses[3], 'jasur@matrix.uz'),
        ]
        for phone, fn, ln, role, wh, email in users_data:
            if not CustomUser.objects.filter(phone=phone).exists():
                CustomUser.objects.create_user(
                    phone=phone, password='User1234!',
                    first_name=fn, last_name=ln, role=role,
                    warehouse=wh, email=email,
                )
        self.stdout.write(f'  Users: {CustomUser.objects.count()}')

        # --- Products ---
        products_data = [
            ('Armatura 12mm', 'Metall buyumlar', 'kg', 14500, 100),
            ('Armatura 16mm', 'Metall buyumlar', 'kg', 15200, 80),
            ('Armatura 20mm', 'Metall buyumlar', 'kg', 15800, 60),
            ('Profil truba 40x20', 'Metall buyumlar', 'm', 28000, 50),
            ('Profil truba 60x40', 'Metall buyumlar', 'm', 42000, 40),
            ('Sement M400', 'Qurilish materiallari', 'ta', 68000, 200),
            ('Sement M500', 'Qurilish materiallari', 'ta', 75000, 150),
            ("G'isht qizil", 'Qurilish materiallari', 'ta', 1200, 5000),
            ("G'isht oq (silikat)", 'Qurilish materiallari', 'ta', 1500, 3000),
            ('Qum (qurilish)', 'Qurilish materiallari', 't', 120000, 50),
            ('Kabel VVG 3x2.5', 'Elektr jihozlari', 'm', 8500, 500),
            ('Kabel VVG 3x1.5', 'Elektr jihozlari', 'm', 5800, 500),
            ('Avtomat 16A', 'Elektr jihozlari', 'ta', 35000, 100),
            ('Rozetka (ikki joy)', 'Elektr jihozlari', 'ta', 18000, 200),
            ('PPR truba 20mm', 'Sanitariya-texnika', 'm', 4500, 300),
            ('PPR truba 32mm', 'Sanitariya-texnika', 'm', 8200, 200),
            ('Kran sharoviy 1/2', 'Sanitariya-texnika', 'ta', 25000, 100),
            ("Bo'yoq oq (10L)", 'Bo\'yoq va kimyoviy', 'ta', 185000, 30),
            ("Lak PF-283 (5L)", 'Bo\'yoq va kimyoviy', 'ta', 95000, 20),
            ('Gruntovka (10L)', 'Bo\'yoq va kimyoviy', 'ta', 65000, 25),
            ('Taxta 40mm', 'Yog\'och materiallari', 'm', 35000, 100),
            ('Faner 18mm', 'Yog\'och materiallari', 'm²', 85000, 50),
            ('Brus 100x100', 'Yog\'och materiallari', 'm', 55000, 40),
        ]
        products = []
        for name, cat_name, unit_abbr, price, min_qty in products_data:
            p, _ = Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': cats[cat_name], 'unit': units[unit_abbr],
                    'price': Decimal(str(price)), 'min_quantity': Decimal(str(min_qty)),
                    'is_active': True,
                }
            )
            products.append(p)
        self.stdout.write(f'  Products: {len(products)}')

        # --- Batches ---
        if Batch.objects.count() == 0:
            batch_list = []
            for product in products:
                for wh in random.sample(warehouses, k=random.randint(1, 3)):
                    qty = Decimal(str(random.randint(5, 500)))
                    min_q = product.min_quantity
                    price = product.price * Decimal(str(random.uniform(0.9, 1.1)))
                    price = price.quantize(Decimal('0.01'))
                    b = Batch(
                        product=product, warehouse=wh, unit=product.unit,
                        quantity=qty, min_quantity=min_q,
                        price=price, description=f'{product.name} — {wh.name}',
                    )
                    batch_list.append(b)

            for b in batch_list:
                b.save()

            # Make some batches LOW or EMPTY for realistic alerts
            low_batches = Batch.objects.order_by('?')[:8]
            for b in low_batches[:5]:
                b.quantity = b.min_quantity - Decimal('1')
                b.save()
            for b in low_batches[5:]:
                b.quantity = Decimal('0')
                b.save()

            self.stdout.write(f'  Batches: {Batch.objects.count()}')
        else:
            self.stdout.write(f'  Batches: {Batch.objects.count()} (already exist)')

        # --- Invoices ---
        if ShotInvoice.objects.count() == 0:
            batches_without_invoice = Batch.objects.filter(invoice__isnull=True)[:15]
            for i, batch in enumerate(batches_without_invoice):
                ShotInvoice.objects.create(
                    invoice_number=f'TTI-{random.randint(1000, 9999)}',
                    batch=batch,
                    warehouse=batch.warehouse,
                    created_by=admin,
                )
            self.stdout.write(f'  Invoices: {ShotInvoice.objects.count()}')

        # --- Orders ---
        if Order.objects.count() == 0:
            customers = [
                'Toshkent Qurilish MCHJ', 'Navoiy Stroy OOO', 'Buxoro Grand Building',
                'IP Saidov A.', 'Farg\'ona Invest Stroy',
            ]
            statuses = ['NEW', 'PROCESSING', 'COMPLETED', 'COMPLETED', 'ON_HOLD']
            for i in range(12):
                wh = random.choice(warehouses)
                order = Order.objects.create(
                    type=random.choice(['INCOMING', 'OUTGOING']),
                    warehouse=wh,
                    created_by=admin,
                    customer_name=random.choice(customers),
                    note=f'Test buyurtma #{i + 1}',
                    status=random.choice(statuses),
                )
                wh_batches = list(Batch.objects.filter(warehouse=wh)[:3])
                for batch in wh_batches:
                    qty = Decimal(str(random.randint(1, 50)))
                    OrderItem.objects.create(
                        order=order, product=batch.product,
                        batch=batch, quantity=qty, price=batch.price,
                    )
                order.calculate_total()
                OrderStatusHistory.objects.create(
                    order=order, status='NEW', note='Buyurtma yaratildi'
                )
                if order.status != 'NEW':
                    OrderStatusHistory.objects.create(
                        order=order, status=order.status, note='Holat yangilandi'
                    )
            self.stdout.write(f'  Orders: {Order.objects.count()}')

        # --- Suppliers ---
        if Supplier.objects.count() == 0:
            supps = [
                ('OOO Tosh Temir Markazi', '123456789', '+998712345678', 'Alisher Navoi'),
                ('MCHJ Global Stroy', '987654321', '+998712345679', 'Sardor Karimov'),
                ('OOO ElektroSnab', '555666777', '+998712345680', 'Nodir Rahimov'),
                ('MCHJ SanitarPlast', '111222333', '+998712345681', 'Jamshid Usmonov'),
                ('OOO BoyoqServis', '444555666', '+998712345682', 'Aziz Toshmatov'),
            ]
            for name, inn, phone, cp in supps:
                Supplier.objects.create(
                    name=name, inn=inn, phone=phone,
                    contact_person=cp, rating=random.randint(3, 5),
                    address='Toshkent shahri',
                )
            self.stdout.write(f'  Suppliers: {Supplier.objects.count()}')

        # --- Construction Objects ---
        if ConstructionObject.objects.count() == 0:
            objs = [
                ("Yunusobod 14-mavze, 9 qavatli uy", 'ACTIVE', 500000000),
                ("Sergeli tuman poliklinikasi ta'miri", 'ACTIVE', 250000000),
                ("Olmazor metro stantsiyasi yaqini", 'PLANNING', 800000000),
                ("Samarqand viloyat shifoxonasi", 'COMPLETED', 350000000),
            ]
            for name, status, budget in objs:
                obj = ConstructionObject.objects.create(
                    name=name, address='Toshkent shahri',
                    start_date=date.today() - timedelta(days=random.randint(30, 180)),
                    budget=Decimal(str(budget)), status=status,
                    responsible_user=admin,
                )
                # Add materials
                for p in random.sample(products, k=min(5, len(products))):
                    planned = Decimal(str(random.randint(50, 500)))
                    used = planned * Decimal(str(random.uniform(0.3, 0.9))) if status != 'PLANNING' else Decimal('0')
                    ObjectMaterial.objects.create(
                        object=obj, product=p, unit=p.unit,
                        planned_quantity=planned, used_quantity=used.quantize(Decimal('0.01')),
                    )
                # Add expenses for ACTIVE/COMPLETED
                if status in ('ACTIVE', 'COMPLETED'):
                    for batch in random.sample(list(Batch.objects.all()[:10]), k=3):
                        ObjectExpense.objects.create(
                            object=obj, batch=batch,
                            quantity=Decimal(str(random.randint(10, 100))),
                            price_per_unit=batch.price,
                            taken_by=admin, warehouse=batch.warehouse,
                        )
            self.stdout.write(f'  Objects: {ConstructionObject.objects.count()}')

        # --- Transfers ---
        if Transfer.objects.count() == 0:
            statuses_t = ['PENDING', 'IN_TRANSIT', 'DELIVERED', 'DELIVERED', 'DELIVERED']
            for i in range(5):
                frm, to = random.sample(warehouses, 2)
                t = Transfer.objects.create(
                    from_warehouse=frm, to_warehouse=to,
                    created_by=admin, status=random.choice(statuses_t),
                    driver_name=f'Haydovchi {i+1}',
                    vehicle_number=f'01A{random.randint(100,999)}AA',
                )
                for batch in random.sample(list(Batch.objects.filter(warehouse=frm)[:5]), k=min(3, Batch.objects.filter(warehouse=frm).count())):
                    TransferItem.objects.create(
                        transfer=t, batch=batch, product=batch.product,
                        quantity=Decimal(str(random.randint(5, 50))),
                    )
            self.stdout.write(f'  Transfers: {Transfer.objects.count()}')

        # --- Estimates ---
        if Estimate.objects.count() == 0:
            est_objs = list(ConstructionObject.objects.all()[:3])
            est_statuses = ['DRAFT', 'APPROVED', 'APPROVED']
            for i, obj in enumerate(est_objs):
                est = Estimate.objects.create(
                    name=f'{obj.name} uchun smeta',
                    object=obj, created_by=admin,
                    status=est_statuses[i % len(est_statuses)],
                    approved_by=admin if est_statuses[i % len(est_statuses)] == 'APPROVED' else None,
                )
                for p in random.sample(products, k=min(5, len(products))):
                    EstimateItem.objects.create(
                        estimate=est, product=p, unit=p.unit,
                        quantity=Decimal(str(random.randint(50, 500))),
                        price_per_unit=p.price,
                    )
                est.calculate_total()
            self.stdout.write(f'  Estimates: {Estimate.objects.count()}')

        # --- Payments ---
        if Payment.objects.count() == 0:
            invoices = list(ShotInvoice.objects.all()[:8])
            for inv in invoices:
                Payment.objects.create(
                    invoice=inv,
                    amount=Decimal(str(random.randint(1000, 50000))),
                    payment_date=date.today() - timedelta(days=random.randint(1, 30)),
                    payment_method=random.choice(['CASH', 'BANK_TRANSFER']),
                    created_by=admin,
                )
            self.stdout.write(f'  Payments: {Payment.objects.count()}')

        self.stdout.write(self.style.SUCCESS('Seed data muvaffaqiyatli yaratildi!'))
