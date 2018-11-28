queries_ = (
    # query 1
    ''' 
    SELECT name as "Drug name", SUM(packs_count) as "Summary packs count"
    FROM public."Drugs" JOIN public."Selling" ON public."Selling".drug_id = public."Drugs".id
    WHERE extract(month from date) = extract(month from now()) and extract(year from date) = extract(year from now())
    GROUP BY name
    ''',
    # query 2
    '''
    SELECT public."Drugs".id as "Drug id", public."Drugs".name as "Drug name", public."Execution Type".name as "Execution type"
    FROM public."Drugs" JOIN public."Execution Type" ON public."Drugs".exec_type_id = public."Execution Type".id
    ''',
    # query 3
    '''
    SELECT extract(month from receipt_date)::int as "Month of receipt date", SUM(amount) as "Amount"
    FROM public."Consignment"
    WHERE extract(year from receipt_date) = extract(year from now())
    GROUP BY extract(month from receipt_date)
    ''',
    # query 4
    '''
    SELECT name as "Drug name"
    FROM public."Drugs"
    WHERE status = 'false'
    ''',
    # query 5
    '''
    SELECT public."Consignment".id as "# consignment", name as "Drug name", extract(day from expiration_date - now())::int AS "Expiration date in days"
    FROM public."Consignment" JOIN public."Drugs" ON public."Consignment".drug_id = public."Drugs".id
    '''
)

description_ = (
    'Number of drugs sold this month',
    'Types of performance drugs',
    'Cost of lots of drugs received in the current year by months',
    'List of drugs that can only be obtained without a prescription',
    'Expiration date of each batch of drugs in days'
)
