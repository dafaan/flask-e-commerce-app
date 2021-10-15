var updatebtns = document.getElementsByClassName('update-cart')
var items = []
for (var i = 0; i < updatebtns.length; i++){
    updatebtns[i].addEventListener('click', function(){
        var product_id = this.dataset.p
        var action = this.dataset.action
        console.log('prod id: ', product_id, 'action: ', action)
        let url = `http://localhost:5000/add_to_cart/${product_id}/`
        fetch(url, {
            method: "POST",   
        })
    })
}