if (window.web3) {
            metamaskWeb3 = new Web3(web3.currentProvider)
            console.log("metamaskweb3", metamaskWeb3);
        }
        else
        {
        	console.log("Download Metamask Please!");
        }

function sendETH(_from, _to, _value)
        {
        		web3.eth.sendTransaction({
            	from: _from,
            	to: _to,
            	value: '100000'
            	}, function(error, hash){
            	    console.log("Hash", hash);
        	});
        }