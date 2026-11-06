(function (root) {
    'use strict';
    function renderOfflineChapters(container, count) {
        if (!container || !Number.isInteger(count) || count < 1 || count > 99) {
            throw new TypeError('Invalid offline course navigation');
        }
        container.textContent = '';
        var notice = document.createElement('p');
        notice.className = 'state-msg';
        notice.textContent = '本地文件模式：可直接打开以下章节；完整课程标题请通过本地 HTTP 服务查看。';
        container.appendChild(notice);
        for (var n = 1; n <= count; n++) {
            var num = String(n).padStart(2, '0');
            var card = document.createElement('div');
            card.className = 'card';
            var link = document.createElement('a');
            link.href = num + '.html';
            link.textContent = '第 ' + num + ' 章 · 开始学习';
            card.appendChild(link);
            container.appendChild(card);
        }
    }
    root.renderOfflineChapters = renderOfflineChapters;
})(typeof window !== 'undefined' ? window : globalThis);
