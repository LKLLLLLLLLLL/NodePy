import { createRouter, createWebHistory, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import Visitor from '@/views/Visitor.vue'
import Home from '@/views/Home.vue'
import File from '@/views/File.vue'
import Program from '@/views/Program.vue'
import Login from '@/views/Login.vue'
import Example from '@/views/Example.vue'
import Editor from '@/views/Editor.vue'

// 定义路由类型
const routes: Array<RouteRecordRaw> = [
    {
        path:'/',
        redirect:'/home'
    },
    {
        path: '/visitor',
        name: 'visitor',
        component: Visitor
    },
    {
        path: '/home',
        name: 'home',
        component: Home
    },
    {
        path: '/file',
        name: 'file',
        component: File
    },
    {
        path: '/program',
        name: 'program',
        component: Program
    },
    {
        path: '/login',
        name: 'login',
        component: Login
    },
    {
        path: '/example',
        name: 'example',
        component: Example
    },
    {
        path: '/editor',
        name: 'editor',
        component: Editor
    }
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
})

export default router