document.addEventListener('DOMContentLoaded', () => {
    const createRuleForm = document.getElementById('createRuleForm');
    const combineRulesForm = document.getElementById('combineRulesForm');
    const evaluateRuleForm = document.getElementById('evaluateRuleForm');
    const resultDiv = document.getElementById('result');
    const treeContainer = document.getElementById('tree-container');

    function renderNode(node) {
        if (!node) return '';

        const nodeElement = document.createElement('div');
        nodeElement.className = 'node';

        const contentElement = document.createElement('div');
        contentElement.className = `node-content ${node.type}-node`;
        contentElement.textContent = node.value;
        nodeElement.appendChild(contentElement);

        if (node.left || node.right) {
            const childrenContainer = document.createElement('div');
            childrenContainer.className = 'node-children';

            if (node.left) {
                const leftChild = document.createElement('div');
                leftChild.className = 'child left-child';
                leftChild.innerHTML = renderNode(node.left);
                childrenContainer.appendChild(leftChild);
            }

            if (node.right) {
                const rightChild = document.createElement('div');
                rightChild.className = 'child right-child';
                rightChild.innerHTML = renderNode(node.right);
                childrenContainer.appendChild(rightChild);
            }

            nodeElement.appendChild(childrenContainer);
        }

        return nodeElement.outerHTML;
    }

    function displayTree(treeData) {
        treeContainer.innerHTML = '';
        if (treeData) {
            const treeHTML = renderNode(treeData);
            treeContainer.innerHTML = `<div class="tree">${treeHTML}</div>`;
        }
    }

    createRuleForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const ruleName = document.getElementById('ruleName').value;
        const ruleString = document.getElementById('ruleString').value;

        try {
            const response = await fetch('/api/rules/create_rule', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ruleName, ruleString }),
            });

            const data = await response.json();
            if (response.ok) {
                resultDiv.textContent = `Rule created successfully. Rule Name: ${data.ruleName}, ID: ${data.id}`;
                displayTree(data.tree);
            } else {
                resultDiv.textContent = `Error: ${data.error}`;
            }
        } catch (error) {
            resultDiv.textContent = `Error: ${error.message}`;
        }
    });

    combineRulesForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const rules = document.getElementById('rules').value.split(',').map(rule => rule.trim());
        const op = document.getElementById('op').value;

        try {
            const response = await fetch('/api/rules/combine_rules', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rules, op }),
            });

            const data = await response.json();
            if (response.ok) {
                resultDiv.textContent = `Rules combined successfully. New Rule Name: ${data.ruleName}, ID: ${data.id}`;
                displayTree(data.tree);
            } else {
                resultDiv.textContent = `Error: ${data.error}`;
            }
        } catch (error) {
            resultDiv.textContent = `Error: ${error.message}`;
        }
    });

    evaluateRuleForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const ast = document.getElementById('ast').value;
        let data;

        try {
            data = JSON.parse(document.getElementById('data').value);
        } catch (error) {
            resultDiv.textContent = 'Invalid JSON data format';
            return;
        }

        try {
            const response = await fetch('/api/rules/evaluate_rule', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ast, data }),
            });

            const result = await response.json();
            if (response.ok) {
                resultDiv.textContent = `Evaluation result: ${result.result}`;
                displayTree(result.tree);
            } else {
                resultDiv.textContent = `Error: ${result.error}`;
            }
        } catch (error) {
            resultDiv.textContent = `Error: ${error.message}`;
        }
    });
});