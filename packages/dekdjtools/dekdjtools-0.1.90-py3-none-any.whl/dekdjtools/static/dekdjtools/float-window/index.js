function addFloatWindow(click, uid) {
    uid = uid || `fw-${Math.floor(Math.random()*2**32)}`
    let elRoot = document.body.querySelector('#' + uid);
    if (!elRoot) {
        elRoot = document.createElement('div');
        elRoot.id = uid;
        elRoot.classList.add('dek-float-window-root');
        document.body.appendChild(elRoot)
    }
    let elPos = null
    let mousedownPos = null
    let elRootStatus = null
    elRoot.style.display = 'none'
    elRoot.style.top = window.innerHeight / 2 + 'px'
    elRoot.style.zIndex = 2 ** 32 - 1 + ''

    const dbClickDelay = 250
    let lastKeyPress = new Date().getTime()
    document.addEventListener('keyup', function (event) {
        if (event.key === 'Control') {
            const now = new Date().getTime()
            if (now - lastKeyPress <= dbClickDelay) {
                dbClickCtr()
            }
            lastKeyPress = now
        }
    })

    document.addEventListener('keydown', function (event) {
        if (elRoot.style.display)
            return
        let direction = null
        if (event.key === 'ArrowDown') {
            if (event.ctrlKey) {
                direction = 1
            }
        } else if (event.key === 'ArrowUp') {
            if (event.ctrlKey) {
                direction = -1
            }
        }
        if (direction != null) {
            moveEl(elRoot.getBoundingClientRect().top + 10 * direction)
            event.preventDefault()
        }
    })

    function dbClickCtr() {
        let queue = [null, 'active']
        elRootStatus = queue[(queue.indexOf(elRootStatus) + 1) % queue.length]
        updateElRoot()
    }

    function updateElRoot() {
        if (elRootStatus == null) {
            elRoot.style.display = 'none'
            elRoot.classList.remove('dek-float-window-root-active')
        } else if (elRootStatus === 'active') {
            elRoot.style.display = ''
            elRoot.classList.add('dek-float-window-root-active')
        }
    }

    function moveEl(y) {
        elRoot.style.top = Math.min(window.innerHeight - elRoot.clientHeight, Math.max(0, y)) + 'px'
    }

    elRoot.addEventListener('mousedown', function (event) {
        elPos = [elRoot.getBoundingClientRect().top, event.pageY]
        mousedownPos = event.pageY
        event.preventDefault()
    })

    document.addEventListener('mousemove', function (event) {
        if (elPos == null)
            return
        event.preventDefault()
        moveEl(elPos[0] + event.pageY - elPos[1])
    })

    document.addEventListener('mouseup', function (event) {
        if (elPos == null)
            return
        event.preventDefault()
        elPos = null
    })

    elRoot.addEventListener('click', function (event) {
        if (mousedownPos !== event.pageY)
            return
        click && click(event)
    })
}
