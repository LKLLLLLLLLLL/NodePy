export type Unit = string;

export interface NumberFieldProps {
  max?: number
  min?: number
  denominator?: number  //  步长分母
  scale?: number  // 小数位数
  width?: string
  height?: string
  disabled?: boolean
  allowEmpty?: boolean
}