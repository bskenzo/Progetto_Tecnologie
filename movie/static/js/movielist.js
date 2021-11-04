function ckChange(ckType){
    let ckName = document.getElementById(ckType.id);
    let filter_price_dec = 'filter_price_dec';
    let filter_price_cre = 'filter_price_cre';

    if (ckName.checked){
        if (!ckName.id.localeCompare(filter_price_dec)) {
            document.getElementById('filter_price_cre').disabled = true;
            document.getElementById('filter_rating').disabled = true;
        }
        else if (!ckName.id.localeCompare(filter_price_cre)){
            document.getElementById('filter_price_dec').disabled = true;
            document.getElementById('filter_rating').disabled = true;
        }
        else {
            document.getElementById('filter_price_dec').disabled = true;
            document.getElementById('filter_price_cre').disabled = true;
        }
    }
    else {
        if (!ckName.id.localeCompare(filter_price_dec)) {
            document.getElementById('filter_price_cre').disabled = false;
            document.getElementById('filter_rating').disabled = false;
        }
        else if (!ckName.id.localeCompare(filter_price_cre)){
            document.getElementById('filter_price_dec').disabled = false;
            document.getElementById('filter_rating').disabled = false;
        }
        else {
            document.getElementById('filter_price_dec').disabled = false;
            document.getElementById('filter_price_cre').disabled = false;
        }
    }
}
