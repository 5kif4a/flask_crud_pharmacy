from main import db
import hashlib
from sqlalchemy.dialects.postgresql import MONEY

views = ('Country list', 'Recipes list', 'Finance report')  # представления
tables = list(set(db.Model.metadata.tables) - set(views))  # все таблицы базы данных


class DrugType(db.Model):  # Тип препарата
    __tablename__ = 'Drug Type'

    def __init__(self, id_, name_):
        self.id = id_
        self.name = name_

    def __repr__(self):
        return '{} {}'.format(self.id, self.name)


class ExecutionType(db.Model):  # Вид исполнения
    __tablename__ = 'Execution Type'

    def __init__(self, id_, name):
        self.id = id_
        self.name = name

    def __repr__(self):
        return '{} {}'.format(self.id, self.name)


class PackagingType(db.Model):  # Вид упаковки
    __tablename__ = 'Packaging Type'

    def __init__(self, id_, name_):
        self.id = id_
        self.name = name_

    def __repr__(self):
        return '{} {}'.format(self.id, self.name)


class ProdCountry(db.Model):  # Страна-производитель
    __tablename__ = 'ProdCountry'

    def __init__(self, id_, name_):
        self.id = id_
        self.name = name_

    def __repr__(self):
        return '{} {}'.format(self.id, self.name)


class Drugs(db.Model):  # Препараты
    __tablename__ = 'Drugs'

    def __init__(self, id_, name_, drug_type_id, exec_type_id, status):
        self.id = id_
        self.name = name_
        self.drug_type_id = drug_type_id
        self.exec_type_id = exec_type_id
        self.status = bool(status)

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.id, self.name, self.drug_type_id, self.exec_type_id, self.status)


class Doctors(db.Model):  # Врачи
    __tablename__ = 'Doctors'

    def __init__(self, id_, name_, med_inst):
        self.id = id_
        self.name = name_
        self.med_institution = med_inst

    def __repr__(self):
        return '{} {} {}'.format(self.id, self.name, self.med_institution)


class Employees(db.Model):  # Сотрудники
    __tablename__ = 'Employees'

    def __init__(self, id_, name_):
        self.id = id_
        self.name = name_

    def __repr__(self):
        return '{} {}'.format(self.id, self.name)


class Selling(db.Model):  # Продажа
    __tablename__ = 'Selling'

    def __init__(self, date, selling_id, employee_id, drug_id, packs_count, amount):
        self.date = date
        self.id = selling_id
        self.employee_id = employee_id
        self.drug_id = drug_id
        self.packs_count = packs_count
        self.amount = amount

    def __repr__(self):
        return '{} {} {} {} {} {}'.format(self.selling_id, self.date, self.employee_id, self.drug_id, self.packs_count, self.amount)


class Recipes(db.Model):  # Рецепты
    __tablename__ = 'Recipes'

    def __init__(self, date, doctor_id, patient_name, drug_id, count, packing_type, recipe_id):
        self.date = date
        self.doctor_id = doctor_id
        self.patient_name = patient_name
        self.drug_id = drug_id
        self.count = count
        self.packing_type = packing_type
        self.id = recipe_id

    def __repr__(self):
        return '{} {} {} {} {} {} {}'.format(self.recipe_id, self.date, self.doctor_id, self.patient_name, self.drug_id,
                                             self.count, self.packing_type)


class Consignment(db.Model):  # Партия
    __tablename__ = 'Consignment'

    def __init__(self, cons_N, drug_id, receipt_date, country_id, manufact_date, expiration_date, packing_id,
                 packs_count, amount, dosage, certificate_N):
        self.id = cons_N
        self.drug_id = drug_id
        self.receipt_date = receipt_date
        self.country_id = country_id
        self.manufact_date = manufact_date
        self.expiration_date = expiration_date
        self.packing_id = packs_count
        self.amount = amount
        self.dosage = dosage
        self.certificate_N = certificate_N

    def __repr__(self):
        return '{} {} {} {} {} {} {} {} {}'.format(self.cons_N, self.drug_id, self.receipt_date, self.country_id,
                                                   self.manufact_date, self.expiration_date, self.packing_id,
                                                   self.amount, self.dosage, self.certificate_N)


class Admin(db.Model):  # Роли
    __tablename__ = 'Admins'

    def __init__(self, id_, login, password):
        self.id = id_
        self.login = login
        self.password = hashlib.sha256(password.encode('utf8')).hexdigest()

    def __repr__(self):
        return '{} {} {}'.format(self.id, self.login, self.password)


class User(db.Model):
    __tablename__ = 'Users'

    def __init__(self, id_, login, password):
        self.id = id_
        self.login = login
        self.password = hashlib.sha256(password.encode('utf8')).hexdigest()

    def __repr__(self):
        return '{} {} {}'.format(self.id, self.login, self.password)


class CountryList(db.Model):  # views
    __tablename__ = 'Country list'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    receipt_date = db.Column(db.Date, nullable=False)
    country = db.Column(db.Text, nullable=False)
    drug_name = db.Column(db.Text, nullable=False)


class FinanceReport(db.Model):
    __tablename__ = 'Finance report'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    employee_name = db.Column(db.Text, nullable=False)
    selling_date = db.Column(db.Date, nullable=False)
    drug_name = db.Column(db.Text, nullable=False)
    packs_count = db.Column(db.Integer, nullable=False)
    amount = db.Column(MONEY, nullable=False)


class RecipesList(db.Model):
    __tablename__ = 'Recipes list'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    drug_name = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    doctor = db.Column(db.Text, nullable=False)
    patient_name = db.Column(db.Text, nullable=False)


def get_class_by_tablename(table_fullname):  # получить модель по имени таблицы
    for c in db.Model._decl_class_registry.values():
        if hasattr(c, '__table__') and c.__table__.fullname == table_fullname:
            return c