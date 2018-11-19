function del(table, id){
    if (confirm('Are you sure want to delete this row?')) {
        location.href = '/tables/' + table + '/delete/' + id;
    };
};